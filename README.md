# Motor de políticas Kyverno en k8s
Bienvenido al TFG sobre la implementación del motor de políticas Kyverno en k8s realizado por el alumno Daniel Miguel Mesa Mejías, del centro IES GONZALO NAZARENO ( 2º ASIR ).

## Tabla de contenido

- [¿Que es Kyverno?](#que-es-kyverno).
- [Cómo trabaja Kyverno](#cómo-trabaja-kyverno).
- [Instalación de Kyverno + K3S](#instalación-de-kyverno-+-k3s).
- [Políticas y reglas](#políticas-y-reglas).
- [Configuración de políticas](#configuración-de-políticas).



### ¿Que es Kyverno?
**Kyverno** es un motor de políticas diseñado para Kubernetes. En **Kyverno**, las políticas se escriben en el mismo lenguaje que la definición de cualquier recurso en Kubernetes y utiliza herramientas con las que ya estamos familiarizados como Git o Kubectl, por lo que que en cuanto a lenguaje y herramientas nos sentiremos mucho más cómodos. Las políticas de **Kyverno** pueden validar, mutar o generar recursos de Kubernetes. Se puede utilizar **Kyverno CLI** para testear políticas o validar recursos como parte de un Pipeline de un CI/CD.



### Cómo trabaja Kyverno
**Kyverno** recibe las respuestas HTTP del webhook configurado (validación,mutación o generación) desde la API de Kubernetes y si la respuesta coincide con alguna política, automáticamente se aplica la política y se procede a admitir o rechazar la petición de Kubernetes.

**Kyverno** puede específicar en sus políticas sobre qué recursos quiere auditar mediante el Kind, nombre o etiquetas, soportando comodines como nombres. Las políticas se aplican sobre recursos que se van a crear, en caso de recursos ya existentes Kyverno notificará aquellos que no cumplan las políticas.

Aquí puedes ver un esquema a alto nivel sobre su funcionamiento:

![Funcionamiento de Kyverno](https://github.com/megandil/k8s-kyverno/blob/main/images/kyverno-architecture.png)

### Instalación de Kyverno + K3S



### Políticas y reglas

Una política de **Kyverno** consiste en una colección de reglas. Cada regla consta de una delaración de "match" o una declaración "exclude", o ambas. Como habrás intuido con "match" se refiere a todo recurso que cumpla la regla y con "exclude" podremos excluir recursos para que se encuentren exentos de cumplir la regla. En la declaración "match" o "exclude" será donde especifiquemos los recursos sobre los que tendrá monitorización Kyverno, podrían tratarse de pods, namespaces,nodos,etc. Cada regla deberá contener un único tipo de declaración, que podría ser de los siguientes tipos: validación (validate), mutación (mutate), generación (generate) o verificación de imágenes (verifyImages).

![Funcionamiento de Políticas](https://github.com/megandil/k8s-kyverno/blob/main/images/Kyverno-Policy-Structure.png)

Los políticas pueden definirse como un recurso del cluster utilizando el Kind "ClusterPolicy" o como un recurso de un namespace determinado utilizando el kind "Policy". Como es de esperar, si se define como un recurso del cluster se aplicará en todos los namespaces que contiene el cluster, sin embargo si se aplica en un namespace solo se aplicará sobre ese namespace seleccionado, esa es la diferencia entre ambas definiciones.



### Configuración de políticas
Como ya sabes, una política contiene una o más reglas, y estos son los parámetros de configuración que podemos aplicar sobre las reglas que conforman una política:

- **ValidationFailureAction**: Si la política es de validación, se pueden configurar 2 modos:
  - **enforce**: Si la petición no cumple la política rechaza la petición y por lo tanto, no valida el recurso.
  - **audit**: Aunque la petición no cumpla la política le permite el acceso validando el recurso, pero informa de la infracción de la política.

- **ValidationFailureActionOverrides**: Es un aributo ClusterPolicy que especifica diferentes "ValidationFailureAction" en función de los namespace existentes.
Anula la funcion de los "ValidationFailureAction" configurados en algún namespace anteriormente.

- **background**: Controla si las políticas creadas se aplican a recursos ya existentes. Por defecto se encuentra configurada en "True".

- **schemaValidation**: Controla si se aplican las comprobaciones de validación de la política. El valor por defecto es "True".
**Kyverno** intentará validar el esquema de una política y fallará si detecta que no cumple la definición del esquema OpenAPI para el determinado recurso.
Este parámetro se puede configurar tanto en una política de validación como una política de mutación, y puede desactivarse si es necesario cambiando el valor a 
"false".

- **failurePolicy**: Con este parámetro podremos configurar el comportamiento del servidor de la API en caso de que el Webhook no responda. Los valores permitidos son "Ignore" o "Fail". Por defecto se encuentra configurado "Fail".

- **webhookTimeoutSeconds**: Especifica el tiempo máximo en segundos permitido para aplicar la política. El tiempo de espera por defecto es de 10s. El valor debe estar entre 1 y 30 segundos.

### Tipos de políticas
Existen 3 tipos de políticas, y son los siguientes:

#### Validación
Las reglas de validación son probablemente los tipos de reglas más comunes y prácticos con los que se trabaja, y el principal tipo de uso para los controladores de admisión como Kyverno.  En una regla de validación, se definen las propiedades obligatorias con las que debe crearse un recurso. Cuando un usuario o proceso crea un recurso, **Kyverno** comprueba las propiedades del recurso con la regla de validación. Si esas propiedades se validan, es decir, si hay coinciden y se realiza el acuerdo entre **Kyverno** y la petición, se permite la creación del recurso. Si esas propiedades son diferentes, la creación se bloquea. El comportamiento de **Kyverno** ante una validación fallida dependerá del valor definido en el campo "validationFailureAction" o "validationFailureActionOverride".Que como expliqué anteriormente puede configurarse para bloquear las peticiones no válidas (enforce) o simplemente auditarlas (audit). Los recursos que infrinjan una regla audit registrarán un evento en el recurso en cuestión.

Como ejemplo, mostraré una política ClusterPolicy que se encargará mediante reglas de validación de comprobar que todos los namespace que se creen contengan la etiqueta "departamento" con el valor "produccion":

```
apiVersion: kyverno.io/v1
# El kind `ClusterPolicy` indica que la política se configura en todo el cluster.
kind: ClusterPolicy
metadata:
  name: requiere-ns-etiqueta-dept
# En `spec` definimoslas propiedades de la política.
spec:
  # El parámetro `validationFailureAction` le dice a Kyverno si permite las peticiones pero las reporta (`audit`) o las bloquea (`enforce`).
  validationFailureAction: enforce
  # En el parámetro `rules` configuramos una o más reglas que se deben cumplir.
  rules:
  - name: requiere-ns-etiqueta-dept
    # En el parámetro `match` declaramos los recursos sobre los que se aplica la política. En este caso en cualquier Namespace.
    match:
      any:
      - resources:
          kinds:
          - Namespace
    # En el parámetro `validate` definimos la regla que se comparará con el recurso. Si lo configurado comparado con el recurso resulta ser verdadero, entonces se permite la petición y se ejecuta, en cambio, si es falsa, se bloquea (dependiendo de "validationFailureAction").
    validate:
      # En `message` definimos el mensaje que queremos que muestre en caso de que la regla no se cumpla.
      message: "Necesitas la etiqueta `departamento` con el valor `produccion` en los nuevos namespaces que vayas a crear."
      # En `pattern` definimos el patrón que será validado en el recurso. En este caso, apuntamos a `metadata.labels` con `departamento=produccion`.
      pattern:
        metadata:
          labels:
            departamento: produccion
  ```

Para aplicar la regla simplemente almacenamos la política en un fichero .yaml y realizamos un:
<pre><code>kubectl apply -f requiere-ns-etiqueta-dept.yaml</code></pre>

Como expliqué anteriormente utiliza kubernetes para la implementación de las políticas por lo que hará uso de "kubectl". Una vez hayamos aplicado la política
intentaremos crear un namespace que no cumpla la política para ver que ocurre:

```
apiVersion: v1
kind: Namespace
metadata:
  name: prod-prueba
  labels:
    departamento: desarrollo
```

Creamos el namespace para ver que sucede:

```
kubectl apply -f namespace-falla-label.yaml
```

Y como no cumple la política nos devolverá el siguiente error:

```
Error from server: error when creating "namespace-falla-label.yaml": admission webhook "validate.kyverno.svc-fail" denied the request: 

resource Namespace//prod-prueba was blocked due to the following policies

requiere-ns-etiqueta-dept:

  requiere-ns-etiqueta-dept: 'validation error: Necesitas la etiqueta `departamento`

    con el valor `produccion` en los nuevos namespaces que vayas a crear. Rule requiere-ns-etiqueta-dept

    failed at path /metadata/labels/departamento/'
```

Para que cumpla la política vamos a cambiar la línea de definición de la etiqueta y vamos a asignar el valor de "produccion":

```
  labels:
    departamento: produccion
```

Intentamos de nuevo crear el namespace y comprobamos que crea el namespace:

```
kubectl apply -f namespace-correcto-label.yaml 

namespace/prod-prueba created
```

Puedes ejecutar esta prueba en la carpeta `/pruebas/validacion` de este repositorio.

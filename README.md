# Motor de políticas Kyverno en k8s
Bienvenido al TFG sobre la implementación del motor de políticas Kyverno en k8s realizado por el alumno Daniel Miguel Mesa Mejías, del centro IES GONZALO NAZARENO ( 2º ASIR ).

## Tabla de contenido

- [¿Que es Kyverno?](#que-es-kyverno).
- [Cómo trabaja Kyverno](#cómo-trabaja-kyverno).
- [Instalación de Kyverno + K3S](#instalación-de-kyverno-y-k3s).
  - [K3S](#k3s).
  - [Kyverno](#kyverno).
- [Políticas y reglas](#políticas-y-reglas).
- [Configuración de políticas](#configuración-de-políticas).
- [Tipos de políticas](#tipos-de-políticas).
  - [Validación](#validación).
  - [Mutación](#mutación).
  - [Generación](#generación).
- [Policy Reporter UI](#policy-reporter-UI).
  - [Instalación](#instalación).
  - [Funcionamiento](#funcionamiento).
    - [Dashboard](#dashboard).



### ¿Que es Kyverno?
**Kyverno** es un motor de políticas diseñado para Kubernetes. En **Kyverno**, las políticas se escriben en el mismo lenguaje que la definición de cualquier recurso en Kubernetes y utiliza herramientas con las que ya estamos familiarizados como Git o Kubectl, por lo que que en cuanto a lenguaje y herramientas nos sentiremos mucho más cómodos. Las políticas de **Kyverno** pueden validar, mutar o generar recursos de Kubernetes. Se puede utilizar **Kyverno CLI** para testear políticas o validar recursos como parte de un Pipeline de un CI/CD.



### Cómo trabaja Kyverno
**Kyverno** recibe las respuestas HTTP del webhook configurado (validación,mutación o generación) desde la API de Kubernetes y si la respuesta coincide con alguna política, automáticamente se aplica la política y se procede a admitir o rechazar la petición de Kubernetes.

**Kyverno** puede específicar en sus políticas sobre qué recursos quiere auditar mediante el Kind, nombre o etiquetas, soportando comodines como nombres. Las políticas se aplican sobre recursos que se van a crear, en caso de recursos ya existentes Kyverno notificará aquellos que no cumplan las políticas.

Aquí puedes ver un esquema a alto nivel sobre su funcionamiento:

![Funcionamiento de Kyverno](https://github.com/megandil/k8s-kyverno/blob/main/images/kyverno-architecture.png)

### Instalación de Kyverno y K3S
A continuación vamos a instalar los dos servicios necesario:

#### K3S
K3S nos proporciona un script de instalación que pone en marcha el cluster automáticamente:

```
curl -sfL https://get.k3s.io | sh -
```

Tras ejecutar ese script tendremos k3s configurado y listo para usar con kubectl. Para ver si el cluster se ha creado correctamente ejecutamos:

```
kubectl get nodes
```

Y nos devolverá algo así (cambiando el nombre por el de tu sistema):

```
NAME     STATUS   ROLES                  AGE    VERSION

debian   Ready    control-plane,master   3d2h   v1.22.7+k3s1
```

Si queremos desinstalar k3s, simplemente ejecutamos el script `k3s-uninstall.sh` alojado en `/usr/local/bin` tras realizar la instalación.


#### Kyverno
Para instalar Kyverno vamos a usar un Chart de Helm:

```
# Añadimos el repositorio Helm
helm repo add kyverno https://kyverno.github.io/kyverno/

# Actualizamos lista de repositorios helm.
helm repo update

# Instalamos el chart de Helm en un nuevo namespace llamado "kyverno"
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
```

Para comprobar que está en funcionamiento vamos a revisar el estado de los Pods del namespace donde hemos instalado Kyverno:

```
kubectl get pods -n kyverno
```

```
NAME                      READY   STATUS    RESTARTS      AGE

kyverno-7fc5f88f8-h5jbr   1/1     Running   5 (48m ago)   3d2h
```

Como podemos ver se encuentra corriendo el pod de Kyverno.

Para ver las políticas aplicadas podemos usar la siguiente instrucción:

```
kubectl get ClusterPolicy
```

```
NAME                        BACKGROUND   ACTION    READY

requiere-ns-etiqueta-dept   true         enforce   true
```

Y para eliminar todas las políticas ejecutamos lo siguiente:

```
kubectl delete cpol --all
```

Para desinstalar Kyverno simplemente ejecutamos el siguiente comando:

```
helm uninstall kyverno kyverno/kyverno --namespace kyverno
```


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

Puedes ejecutar esta prueba con los ficheros alojados en la carpeta `/pruebas/validacion` de este repositorio.



#### Mutación
 
Una regla de mutación puede utilizarse para modificar los recursos que coincidan con la regla y se escribe como un parche JSON RFC 6902 o un "patchStrategicMerge". Si utilizamos un parche JSON, podremos especificar cambios precisos sobre el recurso que estamos creando. Independientemente del método, una regla de mutación se utiliza cuando un objeto necesita ser modificado de una manera determinada.

La mutación de recursos se produce antes de la validación, por lo que las reglas de validación no deben contradecir los cambios realizados por las reglas de mutación.

En el ejemplo que vamos a ver vamos a utilizar una regla de mutación de tipo "patchStrategicMerge", ya que no es necesario mutar el recurso con cambios específiicos al tratarse de una prueba básica. La política de prueba que vamos a aplicar cambia el valor del parámetro "imagePullPolicy" del recurso (pods en este caso) a "IfNotPresent" en caso de que la imagen sea "latest":

```
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: cambiar-image-pull-policy
spec:
  rules:
    - name: cambiar-image-pull-policy
      match:
        any:
        - resources:
            kinds:
            - Pod
      mutate:
        patchStrategicMerge:
          spec:
            containers:
              # Busca coincidencias de recursos que utilicen una imagen con etiqueta latest
              - (image): "*:latest"
                # Establece el valor del parámetro imagePullPolicy a "IfNotPresent"
                imagePullPolicy: "IfNotPresent"
```

Aplicamos la política:

```
kubectl apply -f cambiar-image-pull-policy.yaml 
```

```
clusterpolicy.kyverno.io/set-image-pull-policy created
```

Una vez creado vamos a generar un pod de prueba con el parámetro "imagePullPolicy" con el valor "Always" para ver si al crearlo nos lo cambia. Aquí la definición del pod:

```
apiVersion: v1 
kind: Pod
metadata:        
 name: pod-nginx           
 labels:
   app: nginx
   service: web
spec:
 containers:
   - image: nginx:latest
     name: contenedor-nginx
     imagePullPolicy: Always
```

Y creamos el pod:

```
kubectl apply -f pod.yaml
```

Al generarlo podremos ver como ha descargado la imagen por primera vez utilizando el comando `kubectl describe pod/pod-nginx`:

```
Events:

  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  19s   default-scheduler  Successfully assigned default/pod-nginx to debian
  Normal  Pulling    19s   kubelet            Pulling image "nginx:latest"
  Normal  Pulled     12s   kubelet            Successfully pulled image "nginx:latest" in 6.645054883s
  Normal  Created    12s   kubelet            Created container contenedor-nginx
  Normal  Started    12s   kubelet            Started container contenedor-nginx
```

Y podrás comprobar como el contenedor ha cambiaddo debido a la política de mutación aplicada, observando el valor "IfNotPresent" en el parámetro "imagePullPolicy". Para acceder a ver el valor del parámetro ejecutamos:

```
kubectl get pod pod-nginx -o yaml
```

```
spec:
  containers:
  - image: nginx:latest
    imagePullPolicy: IfNotPresent
    name: contenedor-nginx
```


Si borramos el pod y lo volvemos a crear podremos comprobar que la imagen no se vuelve a descargar ya que al crear el recurso el valor de "imagePullPolicy" está configurado como "IfNotPresent" lo que significa que si la imagen se encuentra en el cluster, no se debe hacer un Pull de nuevo:

```
kubectl describe pod/pod-nginx
```

```
Events:

  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  3s    default-scheduler  Successfully assigned default/pod-nginx to debian
  Normal  Pulled     2s    kubelet            Container image "nginx:latest" already present on machine
  Normal  Created    2s    kubelet            Created container contenedor-nginx
  Normal  Started    2s    kubelet            Started container contenedor-nginx

```

Puedes ejecutar esta prueba con los ficheros alojados en la carpeta `/pruebas/mutacion` de este repositorio.

#### Generación

Las reglas de generación se utilizan para crear un recurso o recursos adicionales cuando se crea un recurso o se modifica se definición (por ejemplo modificar el fichero de definición .yaml de recurso). Resultan útiles para crear recursos de apoyo como RoleBindings o NetworkPolicies para un Namespace.

Las reglas de generación acepta 2 tipos de bloques principales, "match" y "exclude", así como otras reglas no tan destacadas. Por lo tanto, el trigger desencadenante del uso de la política consiste en la generación de recursos, es decir, cuando se genere un recurso y coincida con la política, la aplicará. También es posible hacer coincidir (match) o excluir (exclude) las solicitudes de la API en función de los sujetos, los roles, etc.

La regla de generación solo se aplica cuando realizamos un "Create". Para mantener los recursos sincronizados tras realizar cambios, se puede utilizar el parámetro "synchronize". Cuando la sincronización se establece como "true", el recurso generado se mantiene sincronizado con el recurso de origen (que puede ser definido como parte de la política o puede ser un recurso existente), y los recursos generados no pueden ser modificados por los usuarios. Si la sincronización se establece como "false", los usuarios pueden actualizar o eliminar el recurso generado directamente.

Para probar este tipo de políticas, vamos a generar recursos ResourceQuota y LimitRange por defecto cada vez que se genere un namespace, de tal modo que tendremos controlados los recursos de nuestro cluster.

El fichero de definición de la política es el siguiente:

```
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: quota-ns
  annotations:
    policies.kyverno.io/title: Add Quota
    policies.kyverno.io/category: Multi-Tenancy
    policies.kyverno.io/subject: ResourceQuota, LimitRange
    policies.kyverno.io/description: >-
      Para tener un mayor control sobre el numero de recursos creados en un namespace es recomendable
      asignas recursos ResourceQuota o LimitRange. Esta política genera ambos recursos
      cuando se crea un namespace.      
spec:
  rules:
  - name: generar-resourcequota
    match:
      resources:
        kinds:
        - Namespace
    generate:
      kind: ResourceQuota
      name: resourcequota-default
      synchronize: true
      namespace: "{{request.object.metadata.name}}"
      data:
        spec:
          hard:
            requests.cpu: '4'
            requests.memory: '16Gi'
            limits.cpu: '4'
            limits.memory: '16Gi'
  - name: generar-limitrange
    match:
      resources:
        kinds:
        - Namespace
    generate:
      kind: LimitRange
      name: limitrange-default
      synchronize: true
      namespace: "{{request.object.metadata.name}}"
      data:
        spec:
          limits:
          - default:
              cpu: 500m
              memory: 1Gi
            defaultRequest:
              cpu: 200m
              memory: 256Mi
            type: Container
```

Aplicamos la política:

```
kubectl apply -f quota-limitrange.yaml 

clusterpolicy.kyverno.io/quota-ns created

```

Y para comprobar vamos a crear un namespace cuya definición muestro a continuación:

```
apiVersion: v1
kind: Namespace
metadata:
  name: prueba-generacion
```

Creamos el namespace:

```
kubectl apply -f namespace.yaml 
```

```
namespace/prueba-generacion created
```

Al crearlo realizaremos un "kubectl describe" para obtener los datos del namespace:

```
kubectl describe ns prueba-generacion
```

Y podrás observar como se han establecido las "quotas" y "limitrange":

```
Resource Quotas

  Name:            resourcequota-default
  Resource         Used  Hard
  --------         ---   ---
  limits.cpu       0     4
  limits.memory    0     16Gi
  requests.cpu     0     4
  requests.memory  0     16Gi


Resource Limits
 Type       Resource  Min  Max  Default Request  Default Limit  Max Limit/Request Ratio
 ----       --------  ---  ---  ---------------  -------------  -----------------------
 Container  cpu       -    -    200m             500m           -
 Container  memory    -    -    256Mi            1Gi            -

```

Puedes ejecutar esta prueba con los ficheros alojados en la carpeta `/pruebas/generacion` de este repositorio.


### Policy Reporter UI

Policy Reporter UI es una herramienta gráfica que nos permite ver de una forma más visual y atractiva las reglas de validación de Kyverno. Como ya expliqué anteriormente, Kyverno ofrece dos modos en cuanto a reglas de validación, "enforce" y "audit", pues cuando configuramos en "enforce" bloquea directamente las peticiones pero cuando la regla es de tipo "audit" crea PolicyReports que pueden ser obtenidos mediante Kubectl, pero con esta aplicación veremos ese tipo de reglas de una manera mas amigable mediante una interfaz web.

Con Policy Reporter UI podemos observar qué recursos de nuestro cluster cumplen la reglas que tenemos definidas y qué recursos no las cumplen, de tal manera que podremos detectar errores más rápidamente. En principio, Policy Reporter funciona sin necesidad de tener Kyverno instalado ya que mira los PolicyReports de los ClusterPolicies de k8s, pero en este caso utilizaremos el plugin de Kyverno que trae incorporado Policy Reporter.


#### Instalación

Antes de nada tendremos que crear el namespace donde vamos a realizar la instalación, es importante que el nombre sea "**policy-reporter**".

```
kubectl create ns policy-reporter
```

Y aplicamos los siguientes manifiestos alojados en la carpeta del siguiente [repositorio](https://github.com/megandil/kyverno-argocd/tree/main/policy-ui-reporter-app).

```
kubectl apply -f https://raw.githubusercontent.com/megandil/kyverno-argocd/main/policy-ui-reporter-app/config-secret.yaml
kubectl apply -f https://raw.githubusercontent.com/megandil/kyverno-argocd/main/policy-ui-reporter-app/install.yaml
kubectl apply -f https://raw.githubusercontent.com/megandil/kyverno-argocd/main/policy-ui-reporter-app/ingress.yaml
```

Y solo tendrías que configurarte una entrada en el `/etc/hosts` de tu máquina que reuelva el nombre definido en el ingress, en este caso la entrada es la siguiente:

```
127.0.0.1         www.argocd.org
```

Si quieres cambiar la dirección, deberás modificar el fichero `ingress.yaml` y especificar la que quieras.


#### Funcionamiento

Una vez instalado, podremos acceder a la URL que hemos añadido en nuestro /etc/hosts a través de un navegador web,y nos mostrará el Dashboard de Policy Reporter UI:

![policy reporter ui](https://github.com/megandil/k8s-kyverno/blob/main/images/policy-reporter-ui.png)

##### Dashboard


Como puedes ver, en el dashboard lo que nos aparecen son los elementos del cluster que inflingen las políticas aplicadas de Kyverno, en este caso podemos observar que al namespace "temperaturas" le falta la etiqueta obligatoria "departamento" con el valor "produccion", así que lo primero que haremos será solucionar ese problema y comprobar que desaparece el error del dashboard:

```
  labels:
    departamento: produccion
```

Comprobamos que se ha eliminado el error del dashboard (funciona en tiempo real):

![policy reporter sin errores](https://github.com/megandil/k8s-kyverno/blob/main/images/reporter-sin-errores.png)

La siguiente prueba a realizar será crear un namespace sin esa etiqueta para ver como aparece en el dashboard y se genera un log de error en la página "Logs":

```
kubectl create ns prueba1
```

![reporta error](https://github.com/megandil/k8s-kyverno/blob/main/images/reporta-error.png)

Y se genera un log:

![log error](https://github.com/megandil/k8s-kyverno/blob/main/images/log-error.png)


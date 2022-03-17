# Motor de políticas Kyverno en k8s
Bienvenido al TFG sobre la implementación del motor de políticas Kyverno en k8s realizado por el alumno Daniel Miguel Mesa Mejías, del centro IES GONZALO NAZARENO ( 2º ASIR ).

## Tabla de contenido

- [¿Que es Kyverno?](#que-es-kyverno).
- [Cómo trabaja Kyverno](#cómo-trabaja-kyverno).
- [Políticas y reglas](#políticas-y-reglas).

### ¿Que es Kyverno?
**Kyverno** es un motor de políticas diseñado para Kubernetes. En **Kyverno**, las políticas se escriben en el mismo lenguaje que la definición de cualquier recurso en Kubernetes y utiliza herramientas con las que ya estamos familiarizados como Git o Kubectl, por lo que que en cuanto a lenguaje y herramientas nos sentiremos mucho más cómodos. Las políticas de **Kyverno** pueden validar, mutar o generar recursos de Kubernetes. Se puede utilizar **Kyverno CLI** para testear políticas o validar recursos como parte de un Pipeline de un CI/CD.

### Cómo trabaja Kyverno
**Kyverno** recibe las respuestas HTTP del webhook configurado (validación,mutación o generación) desde la API de Kubernetes y si la respuesta coincide con alguna política, automáticamente se aplica la política y se procede a admitir o rechazar la petición de Kubernetes.

**Kyverno** puede específicar en sus políticas sobre qué recursos quiere auditar mediante el Kind, nombre o etiquetas, soportando comodines como nombres. Las políticas se aplican sobre recursos que se van a crear, en caso de recursos ya existentes Kyverno notificará aquellos que no cumplan las políticas.

Aquí puedes ver un esquema a alto nivel sobre su funcionamiento:

![Funcionamiento de Kyverno](https://github.com/megandil/k8s-kyverno/blob/main/images/kyverno-architecture.png)


### Políticas y reglas

Una política de **Kyverno** consiste en una colección de reglas. Cada regla consta de una delaración de "match" o una declaración "exclude", o ambas. Como habrás intuido con "match" se refiere a todo recurso que cumpla la regla y con "exclude" podremos excluir recursos para que se encuentren exentos de cumplir la regla. En la declaración "match" o "exclude" será donde especifiquemos los recursos sobre los que tendrá monitorización Kyverno, podrían tratarse de pods, namespaces,nodos,etc. Cada regla deberá contener un único tipo de declaración, que podría ser de los siguientes tipos: validación (validate), mutación (mutate), generación (generate) o verificación de imágenes (verifyImages).

![Funcionamiento de Políticas](https://github.com/megandil/k8s-kyverno/blob/main/images/Kyverno-Policy-Structure.png)

Los políticas pueden definirse como un recurso del cluster utilizando el Kind "ClusterPolicy" o como un recurso de un namespace determinado utilizando el kind "Policy". Como es de esperar, si se define como un recurso del cluster se aplicará en todos los namespaces que contiene el cluster, sin embargo si se aplica en un namespace solo se aplicará sobre ese namespace seleccionado, esa es la diferencia entre ambas definiciones.

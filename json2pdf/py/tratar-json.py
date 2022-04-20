import urllib.request, json
with urllib.request.urlopen("http://www.policy-reporter.org/api/result-log") as fichero:
    datos=json.load(fichero)
mensajes=[]
politicas=[]
kinds=[]
nombrekinds=[]
times=[]
for i in datos:
    mensaje=i.get("message")
    mensajes.append(mensaje)
    politica=i.get("policy")
    politicas.append(politica)
    kind=i.get("resource").get("kind")
    kinds.append(kind)
    nombrekind=i.get("resource").get("name")
    nombrekinds.append(nombrekind)
    time=i.get("creationTimestamp")
    times.append(time)

print("= HISTORIAL DE LOGS")
print()
for o,i,a,b,c,d in zip(range(len(mensajes)),mensajes,politicas,kinds,nombrekinds,times):
    print('=== LOG' ,o,' ===')
    print()
    print()
    print('*Mensaje*: ',i)
    print()
    print('*Politica*: ',a)
    print()
    print('*Tipo de objeto afectado*: ',b)
    print()
    print('*Nombre de objeto afectado*: ',c)
    print()
    print('*Fecha de creacion*: ',d)
    print()
    print()


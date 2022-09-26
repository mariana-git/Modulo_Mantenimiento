from email.message import EmailMessage
from random import choices
from django.db.models import Q,Sum
from requests import delete   
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django .contrib import messages
from datetime import date
from sis.settings import EMAIL_HOST_USER

#region----------- VIEWS INDEX---------------------------------
def index(request):
   p,t,i,c=0,0,0,0
   today = date.today()
   p = proveedores.objects.all().count()
   t = tickets.objects.all().count()
   i = inspecciones.objects.all().count()
   count_record_hoy = recordatorio.objects.filter(fecha__lte=today, fecha__gte=today).count()
   count_cap_hoy = capacitaciones.objects.filter(fecha__gte=today).count()
   c= count_record_hoy + count_cap_hoy
   data = { 
      'p' :  p,
      't' :  t,
      'i' :  i,
      'c' :  c,
      }
   return render(request,'modulo4/index.html', data)
#endregion


#region----------- VIEW SEDES ----------------------------------

def agregarSede(request):

   data = {
      'form': SedesForm(),
      'accion':'Crear',
   }

   if request.method == 'POST':
      formulario = SedesForm(data=request.POST, files=request.FILES)
      if formulario.is_valid():
         formulario.save()
         getid = formulario.save()
         messages.success(request, "Agregado correctamente.")
         return redirect(to='detalle_sede',id=getid.id)
      else:
         messages.error(request, "No se pudo agregar.")
         data["form"] = formulario
         
   return render(request, 'modulo4/sedes/form_sede.html', data)

def detalleSede (request, id):

   sede = get_object_or_404(sedes_info, id=id)

   if request.method == 'POST':

      if 'borrar_sede' in request.POST:
         sede.delete()
         messages.success(request, "Borrado correctamente.")
         return redirect(to='listar_sede')
      else:
         messages.error(request, "No se pudo borrar la sede.")

   data = {
      'sede':sede,
      }

   return render(request, 'modulo4/sedes/detalle_sede.html',data)

def listarSede(request):
   sedes = sedes_info.objects.all().order_by('short_name')
   
   data = {
      'sedes': sedes
   }
   
   return render(request,'modulo4/sedes/listar_sede.html', data)

def modificarSede(request, id):
   
   sede = get_object_or_404(sedes_info, id=id)

   data = {
      'form': SedesForm(instance=sede),
      'sede' : sede,
      'accion':'Modificar',
   }
   
   
   if request.method == 'POST':
      formulario = SedesForm(data=request.POST, instance=sede, files=request.FILES)
      if formulario.is_valid():
         formulario.save()
         getid = formulario.save()
         messages.success(request, "Modificado correctamente.")
         return redirect(to='detalle_sede', id=getid.id)
      else:
         data["form"] = formulario
         messages.error(request, "No se pudo modificar.")
   
   
   return render(request, 'modulo4/sedes/form_sede.html', data)


#endregion


#region----------- VIEW ESTADOS (de tickets, ot, cotizaciones, etc) -------------------------------
def cambiarEstado(request,id,origen):
   
   form= EstadosForm(origen)
   

   data = {
      'form': form,
      'identificador': id,
   }
   return render(request,'modulo4/estados/cambiar_estado.html',data)
#endregion


#region----------- VIEW TICKETS -------------------------------
def consultarTicket(request,id):
   ot_estados, ot_adjuntos, cotiz, calif={},{},{},0

   #----------data ticket
   ticket = get_object_or_404(tickets, id=id)   
   tk_adjuntos = archivos.objects.filter(referencia ='TICKET',identificador=id)
   tk_estados = estados.objects.filter(referencia ='TICKET',identificador=id)
   opcion_borrado = 'Orden Trab.' if ticket.estado_actual == 'ACEPTADO' else 'Ticket'  #data para el boton modal de borrado
   
  
   

   #----------data ot   
   ot = ordenes_de_trabajo.objects.filter(ticket=id).first()    
   if ot:      
      cotiz = cotizaciones.objects.filter(ot=ot.id)
      ot_estados = estados.objects.filter(referencia ='OT',identificador=ot.id)
      ot_adjuntos = archivos.objects.filter(referencia ='OT',identificador=ot.id)
      
      #control de los dias de la OT
      if ot.estado_actual!='FINALIZADA': 
         if ot.demora():
            ot.estado_actual='DEMORADA'
            ot.save()
         elif ot.restantes():         
            ot.estado_actual='EN EJECUCIÓN'
            ot.save()
      #----------data calificacion
      calif=calificacion.objects.filter(referencia = 'OT', identificador=ot.id).first()
   
   #--------data cotizaciones
   info_cotizaciones = {}
   if cotiz:
      info_cotizaciones= {
         'total' : cotiz.count(),       
         'en_espera' : cotiz.filter(estado_actual__contains = 'ENVIADA').count(),    
         'rechazadas' : cotiz.filter(estado_actual__contains = 'RECHAZADA').count(),     
         'en_revision' : cotiz.filter(estado_actual__contains = 'EN REVISION').count(),          
         'aceptada' : cotiz.filter(estado_actual__contains = 'ACEPTADA').first(),         
      }  
      
   if request.method == 'POST':

      if 'calificar' in request.POST:
         identificador = request.POST.get('identificador')
         ref = request.POST.get('referencia')
         puntos = request.POST.get('cal')
         calificacion.objects.create(
            usuario = 'usuarioActual',
            referencia = ref,
            identificador= identificador,
            puntos = puntos,
         )
         messages.success(request, "Calificación guardada.")
         return redirect(to='ticket', id=id)
         

      elif 'borrado' in request.POST:
         objeto = request.POST.get('objeto_borrar')
         id_objeto = request.POST.get('id_objeto_borrar')


         if objeto =='borrar_Ticket':
            if ticket.estado_actual == 'ACEPTADO':
               messages.warning(request, "No se puede borrar Ticket ACEPTADO")
            else:
               tk_estados.delete()
               tk_adjuntos.delete()
               ticket.delete()            
               messages.success(request, "Borrado correctamente.")
               return redirect(to='listar_tickets')

         elif objeto == 'borrar_Orden Trab.':   
            if ot.estado_actual != 'COTIZANDO':
               messages.warning(request, "No se puede borrar OT vigente")
            else:         
               ticket.estado_actual = 'EN EVALUACION'
               ot_estados.delete()
               for c in cotiz:
                  estados.objects.filter(referencia='COTIZACIÓN',identificador = c.id).delete()
               if calif: calif.filter(referencia='OT',identificador = ot.id).delete()
               cotiz.delete()            
               ot.delete()            
               ticket.save()

               # guardo datos en la tabla de estados
               estados.objects.create(
               referencia = 'TICKET',
               identificador = ticket.id,
               estado = 'EN EVALUACION' ,   
               motivo = 'Cancelación de la O.T.',
               )
               messages.success(request, "Borrado correctamente.")
               return redirect(to='ticket', id=id)
         
         elif objeto == 'borrar_cotizacion':
            cotizacion = cotizaciones.objects.get(id=id_objeto)

            if cotizacion.estado_actual == 'ACEPTADA':
               messages.warning(request, "No se puede borrar una cotización ACEPTADA.")
            else:               
               cotizacion.delete()
               estados.objects.filter(referencia = 'COTIZACIÓN',identificador = id_objeto).delete()
               archivos.objects.filter(referencia = 'COTIZACIÓN',identificador = id_objeto).delete()
               messages.success(request, "Borrada correctamente.")
               return redirect(to='ticket', id=id)

         elif objeto == 'borrar_estado_tk':  #borrado de estados
           
            if ticket.estado_actual == 'ACEPTADO':               
               messages.warning(request, "No se puede borrar: ticket ACEPTADO.")
            else:
               tk_estados.get(id = id_objeto).delete()
               messages.success(request, "Borrado correctamente.")
               return redirect(to='ticket', id=id)

         elif objeto == 'borrar_estado_ot':
            if ot.estado_actual == 'FINALIZADA':               
               messages.warning(request, "No se puede borrar: OT FINALIZADA.")
            else:
               ot_estados.filter(referencia = 'OT',id = id_objeto).delete()
               messages.success(request, "Borrado correctamente.")
               return redirect(to='ticket', id=id)
         
         elif objeto[:7] == 'archivo': #borrado de archivos
               ref = objeto[8:]
               archivos.objects.get(referencia = ref ,id = id_objeto).delete()
               messages.success(request, "Borrado correctamente.")
               return redirect(to='ticket', id=id)
         
               
      elif 'cambiar_estado' in request.POST:
         ref = request.POST.get('referencia')
         formulario = EstadosForm(ref,data=request.POST, files=request.FILES)
         files = request.FILES.getlist('archivos')
         if formulario.is_valid():

            if ref == 'TICKET':
               ticket.estado_actual = request.POST.get('estado')
               get_tk = ticket.save()

               # si tiene adjuntos los guardo en la tabla archivos
               for f in files:
                  archivos.objects.create(
                     referencia = ref,
                     identificador = ticket.id,
                     archivo = f,
                     nombre = f.name,
                     tipo = f.content_type,
                  )      

               # si el Ticket fue aceptado creo una nueva instancia de OT 
               if ticket.estado_actual == 'ACEPTADO':
                  get_ot = ordenes_de_trabajo.objects.create(
                  ticket = ticket,
                  estado_actual = 'COTIZANDO',
                  reprogramaciones=0,
               ) 

                  # guardo datos en la tabla estados para esa nueva OT
                  estados.objects.create(
                  referencia = 'OT',
                  identificador = get_ot.id,
                  estado = get_ot.estado_actual,       
                  motivo = 'Ticket aceptado.',
                  )  

            elif ref == 'OT':
               estado = request.POST.get('estado')              

               if estado != 'COTIZANDO' and not cotiz.filter(estado_actual = 'ACEPTADA').exists():
                  messages.warning(request, "No existe cotizacion ACEPTADA.")
                  return redirect(to='ticket', id=id)
               
               elif estado == 'EN EJECUCIÓN':
                  if ot.estado_actual== 'EN EJECUCIÓN':
                     messages.warning(request, "la OT ya se encuentra EN EJECUCIÓN.")
                     return redirect(to='ticket', id=id)
                  elif ot.estado_actual== 'FINALIZADA':
                     ot.fecha_finalizacion == None
                     ot.save()
                  elif not ot.fecha_inicio: 
                     ot.fecha_inicio = date.today()

               elif estado == 'FINALIZADA':
                  if ot.estado_actual== 'FINALIZADA':
                     messages.warning(request, "la OT ya se encuentra FINALIZADA.")
                     return redirect(to='ticket', id=id)
                  else: 
                     ot.fecha_finalizacion = request.POST.get('fecha_finalizacion')
                     ot.save()
               
               ot.estado_actual = estado                     
               ot.save()
               
               # si tiene adjuntos los guardo en la tabla archivos
               for f in files:
                  archivos.objects.create(
                     referencia = ref,
                     identificador = ot.id,
                     archivo = f,
                     nombre = f.name,
                     tipo = f.content_type,
                  ) 
            
            formulario.save()

            messages.success(request, "Estado actualizado.")
            return redirect(to='ticket', id=id)
         else:
            messages.error(request, "No se pudo actualizar.") 


      elif 'agregar_cotizacion' in request.POST:
         formulario = CotizacionesForm(data=request.POST, files=request.FILES)
         files = request.FILES.getlist('archivos')

         if formulario.is_valid():
            get_cotiz = formulario.save()

            # si tiene adjuntos los guardo en la tabla archivos
            for f in files:
               archivos.objects.create(
                  referencia = 'COTIZACIÓN',
                  identificador = get_cotiz.id,
                  archivo = f,
                  nombre = f.name,
                  tipo = f.content_type,
               )      

            # guardo una entrada en la tabla estados
            estados.objects.create(
            referencia = 'COTIZACIÓN',
            identificador = get_cotiz.id,
            estado = get_cotiz.estado_actual,       
            motivo = 'Solicitud de cotización.',
         )      
            messages.success(request, "Cotización agregada.")
            return redirect(to='ticket', id=id)
         else:
            messages.error(request, "No se pudo agregar.")  


      elif 'actualizar_cotizacion' in request.POST:  
         formulario = EstadosForm(data=request.POST)
         if formulario.is_valid():
            formulario.save()
         messages.success(request, "Estado actualizado.")
         return redirect(to='ticket', id=id)

      else:
         messages.error(request, "No pudo realizarse la acción.")
   data = {
      'ticket': ticket,
      'opcion_borrado': opcion_borrado,
      'tk_estados':tk_estados,
      'ot_estados': ot_estados,
      'tk_adjuntos': tk_adjuntos,
      'ot_adjuntos': ot_adjuntos,
      'form_cotizaciones': CotizacionesForm(),
      'cotizaciones':cotiz,
      'info_cotizaciones': info_cotizaciones,
      'ot': ot,
      'hoy': datetime.today().date(),
      'calificacion': calif if calif else None,
   }

   return render(request,'modulo4/tickets/ticket.html', data)


def agregarTicket(request):
   sedes = sedes_info.objects.all()
   
   data = { 
      'form':TicketsForm(),      
      'accion': 'Agregar',
      'sedes':sedes,
      }

   if request.method == 'POST':
      formTicket = TicketsForm(data=request.POST, files=request.FILES)      
      files = request.FILES.getlist('archivos')
      
      if formTicket.is_valid():
         get_tk = formTicket.save()

         # guardo datos en la tabla Estados
         estados.objects.create(
            referencia = 'TICKET',
            identificador = get_tk.id,
            estado = get_tk.estado_actual,       
            motivo = 'Solicitud de mantenimiento.',
         )      

         # guardo archivos en la tabla archivos         
         for f in files:
            archivos.objects.create(
               referencia = 'TICKET',
               identificador = get_tk.id,
               archivo = f,
               nombre = f.name,
               tipo = f.content_type,
            )           

         messages.success(request, "Agregado correctamente.")
         return redirect(to='ticket',id=get_tk.id)
      else:
         messages.error(request, "No se pudo agregar.")         
         
   return render(request,'modulo4/tickets/form_ticket.html', data)
    

def modificarTicket(request, id):

   ticket = get_object_or_404(tickets, id=id)  
   tk_adjuntos = archivos.objects.filter(referencia='TICKET',identificador=id)

   if ticket.estado_actual == 'RECHAZADO' or ticket.estado_actual == 'INSPECCIÓN PENDIENTE':
      messages.error(request, "No se puede modificar un Ticket en esta instancia.") 
      return redirect(to='ticket', id=id)
   else:
      if request.method == 'POST':
         formulario = TicketsForm(instance=ticket, data=request.POST, files=request.FILES)
         files = request.FILES.getlist('archivos')
         
         if formulario.is_valid():
            get_tk= formulario.save()

            # guardo archivos en la tabla archivos         
            for f in files:
               archivos.objects.create(
                  referencia = 'TICKET',
                  identificador = id,
                  archivo = f,
                  nombre = f.name,
                  tipo = f.content_type,
               )           
            messages.success(request, "Modificado correctamente.")
            return redirect(to='ticket', id=id)
         else:
            messages.error(request, "No se pudo editar.")         
         
   
   data = { 
      'form':TicketsForm(instance=ticket),
      'tk_adjuntos': tk_adjuntos,
      'accion': 'Modificar',
      'ticket': ticket,
      }
   return render(request,'modulo4/tickets/form_ticket.html', data)


def buscarTicket(request):

   listar_tkts = tickets.objects.all()
   listar_ot = ordenes_de_trabajo.objects.all()
   sedes = sedes_info.objects.all()

   if request.method == 'POST':
      q = request.POST
      for k,v in q.items(): 
         if v:
            if k =='sede': listar_tkts = listar_tkts.filter(sede__nombre = v)
            if k =='trabajo_req': listar_tkts = listar_tkts.filter(trabajo_req = v)
            if k =='categoria': listar_tkts = listar_tkts.filter( categoria= v)
            if k =='prioridad': listar_tkts = listar_tkts.filter( prioridad= v) 
            if k =='riesgo': listar_tkts = listar_tkts.filter(riesgo = v)
            if k =='seguridad': listar_tkts = listar_tkts.filter( seguridad= v)
            if k =='estado_actual': listar_tkts = listar_tkts.filter( estado_actual= v)

      if listar_tkts:        
         messages.success(request, "Resultado de busqueda")
      else:
         messages.error(request, "No se encontraron resultados.")    

   data = { 
      'tickets': listar_tkts,
      'sedes':sedes,
      'ttrabajo_req':CHOICE_TIPO_TRABAJO,
      'tcategoria':CHOICE_CATEGORIA,
      'tprioridad':CHOICE_IMPACTO,
      'triesgo':CHOICE_IMPACTO,
      'tseguridad':CHOICE_IMPACTO,
      'testado_actual':CHOICE_ESTADO_TICKET,
      'listar_ot': listar_ot,
      }   
   
   return render(request,'modulo4/tickets/buscar_ticket.html', data)


def listarTickets(request):

   listar_tkts = tickets.objects.all()
   listar_ots= ordenes_de_trabajo.objects.all()
   data = { 
      'tickets': listar_tkts,
      'ots':listar_ots,
      }
   return render(request,'modulo4/tickets/listar_tickets.html', data)
   
#endregion


#region----------- VIEW VISOR DE IMAGENES -----------------------------
def verImagenes(request, id,ref):
   seleccionada = archivos.objects.get(referencia = ref,id=id)
   imagenes = archivos.objects.filter(tipo__icontains = 'image',referencia = ref, identificador= seleccionada.identificador)
   imagenes = imagenes.exclude(nombre= seleccionada.nombre)
   obj=None
   if ref=='OT': 
      ot=ordenes_de_trabajo.objects.get(id=seleccionada.identificador)
      obj = ot.ticket.id
   elif ref =='VISITA':
      v = ot=visitas.objects.get(id=seleccionada.identificador)
      obj = v.inspeccion.id
   else: 
      obj = seleccionada.identificador


      
   data = { 
      'imagenes': imagenes,
      'seleccionada':seleccionada,
      'obj': obj,
      }

   return render(request,'modulo4/visorImagenes/ver_imagenes.html', data)
#endregion


#region----------- VIEW COTIZACIONES -------------------------------
def detalleCotizacion(request,id):

   form= EstadosForm('COTIZACIÓN')
   cotizacion = cotizaciones.objects.get(id=id)
   cotizacion_estados = estados.objects.filter(referencia = 'COTIZACIÓN', identificador = id)
   ct_adjuntos = archivos.objects.filter(referencia = 'COTIZACIÓN', identificador = id)
   ot = ordenes_de_trabajo.objects.get(id=cotizacion.ot.id)
   ticket = cotizacion.ot.ticket.id

   if request.method == 'POST':
      
      if 'cambiar_estado' in request.POST:
         ref = request.POST.get('referencia')
         formulario = EstadosForm(ref,data=request.POST, files=request.FILES)
         files = request.FILES.getlist('archivos')
         
         if formulario.is_valid():
            nuevo_estado = request.POST.get('estado')

            if nuevo_estado == 'ACEPTADA':
               if cotizacion.estado_actual == 'ACEPTADA':
                  messages.warning(request, "El estado actual ya es ACEPTADA.")
                  return redirect(to='detalle_cotizacion', id=id)

               
               elif ot.estado_actual != 'COTIZANDO':
                  messages.warning(request, "La OT ya tiene una cotización aceptada.")
                  return redirect(to='detalle_cotizacion', id=id)


               else:
                  # Si la cotizacion pasa a estar ACEPTADA, actualizo la OT a COTIZANDO
                  ot.fecha_asignacion = datetime.now()
                  ot.proveedor_asignado = proveedores.objects.get(id=cotizacion.proveedor.id)
                  ot.estado_actual = 'ASIGNADA'
                  ot.save()

                  # guardo una entrada para la ot en la tabla estados
                  estados.objects.create(
                  referencia = 'OT',
                  identificador = ot.id,
                  estado = ot.estado_actual,       
                  motivo = 'Aceptación de la cotización.',
                  )

            else:               
               if cotizacion.estado_actual == 'ACEPTADA':

                  # quito las referencias en la OT
                  ot.fecha_asignacion = None
                  ot.proveedor_asignado = None
                  ot.fecha_inicio = None
                  ot.fecha_fin_prevista = None
                  ot.fecha_finalizacion = None
                  ot.presup_aprobado = None
                  ot.presup_ejecutado = None
                  ot.presup_en_ejecucion = None
                  ot.estado_actual = 'COTIZANDO'
                  ot.save()

                  # guardo una entrada para la OT en la tabla estados
                  estados.objects.create(
                  referencia = 'OT',
                  identificador = ot.id,
                  estado = ot.estado_actual,       
                  motivo = 'Cancelación de la asignación.',
                  )  

                 
            # si tiene adjuntos los guardo en la tabla archivos
            for f in files:
               archivos.objects.create(
                  referencia = ref,
                  identificador = cotizacion.id,
                  archivo = f,
                  nombre = f.name,
                  tipo = f.content_type,
               )  

            cotizacion.estado_actual = nuevo_estado
            cotizacion.save()
            formulario.save()            
            messages.success(request, "Estado actualizado.")
            return redirect(to='ticket',id=ticket)
         
         else:
            messages.error(request, "Datos no válidos.")
      
      
      elif 'borrado' in request.POST:
         
         #si la cotizacion estaba ACEPTADA, actualizo la OT
         if cotizacion.estado_actual == 'ACEPTADA':
            ot.fecha_asignacion = None
            ot.categoria = None
            ot.proveedor_asignado = None
            ot.save()

            # guardo una entrada para la ot en la tabla estados
            estados.objects.create(
            referencia = 'OT',
            identificador = ot.id,
            estado = 'COTIZANDO',       
            motivo = 'Por baja de cotización.',
            )   
         
         id_obj = request.POST.get('id_objeto_borrar')

         cotizacion_estados.filter(referencia = 'COTIZACIÓN',id = id_obj).delete()
         ultima = cotizacion_estados.first()
         cotizacion.estado_actual = ultima.estado
         cotizacion.save()
   

         messages.success(request, "Borrado correctamente.")
            
      else:
         messages.error(request, "No se pudo actualizar.") 

      
   data = {
      'form': form,
      'cotizacion': cotizacion,
      'cotizacion_estados':cotizacion_estados,
      'ct_adjuntos': ct_adjuntos,
      'ticket': ticket,
   }
   return render(request,'modulo4/tickets/detalle_cotizacion.html',data)
#endregion


#region----------- VIEW OT -----------------------------
def modificarOT(request,id):
   fp_ot, fp_post = None,None #para el control de reprogramaciones
   ot = get_object_or_404(ordenes_de_trabajo, id=id)  
   if ot.fecha_fin_prevista: fp_ot= ot.fecha_fin_prevista.date() #para el control de reprogramaciones

   if ot.estado_actual == 'FINALIZADA':
       messages.error(request, "No puede editarse una Orden FINALIZADA.")  
       return redirect(to='ticket', id=ot.ticket.id)
   else:
      ot_adjuntos = archivos.objects.filter(referencia='OT',identificador=id)
      
      data = { 
         'form':OTForm(instance=ot),
         'ot_adjuntos': ot_adjuntos,
         'ot': ot,
         }

      if request.method == 'POST':
         formulario = OTForm(instance=ot,data=request.POST, files=request.FILES)
         files = request.FILES.getlist('archivos')
         if formulario.is_valid():

            # guardo archivos en la tabla archivos         
            for f in files:
               archivos.objects.create(
                  referencia = 'OT',
                  identificador = id,
                  archivo = f,
                  nombre = f.name,
                  tipo = f.content_type,
               )    
            getid=formulario.save()  

            #control de reprogramaciones
            if getid.fecha_fin_prevista: fp_post= getid.fecha_fin_prevista.date()
            if fp_ot and fp_post:
               if  fp_ot > fp_post or fp_ot < fp_post:
                  getid.reprogramaciones +=1
                  getid.save()
            elif fp_ot and not fp_post:                
                  getid.reprogramaciones +=1
                  getid.save()

            if  getid.fecha_inicio: 
               if getid.fecha_inicio.date() < datetime.today().date():
                  ot.estado_actual='EN EJECUCIÓN'
                  ot.save()

            messages.success(request, "Modificado correctamente.")
            return redirect(to='ticket', id=ot.ticket.id)
         else:
            messages.error(request, "No se pudo editar.")         
            
      return render(request,'modulo4/tickets/form_ot.html', data)


#endregion--------------------------------------------------------


#region----------- VIEW INSPECCIONES ------------------------------
def verInspeccion(request,id):
   v,i,acta, vis_adjuntos,vis_estados,insp_adjuntos,insp_estados = [],[],[],[],[],[],[]
   i=inspecciones.objects.filter(id=id).first()
   v=visitas.objects.filter(inspeccion=id).first()
   if v: acta=actasDeInspeccion.objects.filter(visita=v.id).first()
   
   if v:
      vis_adjuntos=archivos.objects.filter(referencia='VISITA', identificador=id)
      vis_estados=estados.objects.filter(referencia='VISITA', identificador=id)
      if v.fecha_visita and not acta:
         if v.fecha_visita.date() < datetime.today().date():
            v.estado_actual='DEMORADA'
            v.save()
   insp_adjuntos=archivos.objects.filter(referencia='INSPECCIÓN', identificador=id)
   insp_estados=estados.objects.filter(referencia='INSPECCIÓN', identificador=id)
   opcion = 'Visita' if i.estado_actual == 'ACEPTADA' else 'Inspección'  #data para el boton modal de borrado
   
   data = {
      'i': i,
      'v': v,
      'acta':acta,
      'insp_adjuntos':insp_adjuntos,
      'insp_estados':insp_estados,  
      'vis_adjuntos':vis_adjuntos,
      'vis_estados':vis_estados,
      'opcion':opcion,
   }

   if request.method == 'POST':
      if 'borrado' in request.POST:
         objeto = request.POST.get('objeto_borrar')
         id_objeto = request.POST.get('id_objeto_borrar')

         if objeto =='inspección':
            if i.estado_actual == 'ACEPTADA':
               messages.warning(request, "No se puede borrar una inspección ACEPTADA")
            else:
               insp_estados.delete()
               insp_adjuntos.delete()
               i.delete()            
               messages.success(request, "Borrado correctamente.")
               return redirect(to='listar_inspecciones')

         elif objeto =='visita':
            if v.estado_actual == 'FINALIZADA':
               messages.warning(request, "No se puede borrar una visita FINALIZADA")
            else:
               vis_estados.delete()
               vis_adjuntos.delete()
               v.delete()
               i.estado_actual = 'EN EVALUACIÓN' 
               i.save()

               # guardo datos en la tabla de estados
               estados.objects.create(
               referencia = 'INSPECCIÓN',
               identificador = id,
               estado = i.estado_actual ,   
               motivo = 'Visita eliminada.',
               )
               messages.success(request, "Borrado correctamente.")

         elif objeto =='estado_inspeccion':
            if i.estado_actual == 'ACEPTADA' or i.estado_actual == 'FINALIZADA':
               messages.warning(request, "No se puede modificar una inspección "+ i.estado_actual)
            else:
               insp_estados.get(id = id_objeto).delete()
               messages.success(request, "Borrado correctamente.")

         elif objeto =='estado_visita':
            if v.estado_actual == 'PROGRAMADA' or v.estado_actual == 'FINALIZADA':
               messages.warning(request, "No se puede modificar una inspección "+ v.estado_actual)
            else:
               vis_estados.get(id = id_objeto).delete()
               messages.success(request, "Borrado correctamente.")

      elif 'cambiar_estado' in request.POST:
         ref = request.POST.get('referencia')         
         est_form = request.POST.get('estado')
         formulario = EstadosForm(ref,data=request.POST, files=request.FILES)
         files = request.FILES.getlist('archivos')   

         if formulario.is_valid():
            getid = formulario.save()

            if ref =='INSPECCIÓN':      
               # guardo archivos en la tabla archivos         
               for f in files:
                  archivos.objects.create(
                     referencia = ref,
                     identificador = i.id,
                     archivo = f,
                     nombre = f.name,
                     tipo = f.content_type,
                  )     
               if est_form =='ACEPTADA' and i.estado_actual != est_form:
                  # creo un objeto en la tabla de visitas
                  visitas.objects.create(
                  inspeccion = i,
                  estado_actual = 'A DEFINIR',
                  )
               i.estado_actual= est_form
               i.save()

               messages.success(request, "Agregado correctamente.")
               return redirect(to='ver_inspeccion',id=id)

            elif ref =='VISITA': 
               if v.estado_actual == 'FINALIZADA':
                  messages.warning(request, "No se puede modificar una visita FINALIZADA")
               else:
                  # guardo archivos en la tabla archivos         
                  for f in files:
                     archivos.objects.create(
                        referencia = ref,
                        identificador = v.id,
                        archivo = f,
                        nombre = f.name,
                        tipo = f.content_type,
                     ) 
                  if est_form =='PROGRAMADA':
                     v.fecha_visita = request.POST.get('fecha_visita')       
                     
                  v.estado_actual= est_form
                  v.save()
                  messages.success(request, "Agregado correctamente.")
                  return redirect(to='ver_inspeccion',id=id)
         else:
            messages.error(request, "No se pudo realizar la acción.")
            data["form"] = formulario

   return render(request, 'modulo4/inspecciones/ver_inspeccion.html',data)

def listarInspecciones(request):
   insp=inspecciones.objects.all()
   vis=visitas.objects.all()
   actas=actasDeInspeccion.objects.all()

   data = { 
      'insp' :  insp,
      'vis':vis,
      'actas':actas,
      }

   return render(request, 'modulo4/inspecciones/listar_inspecciones.html',data)

def agregarInspeccion(request):

   if request.method == 'POST':
      formulario = InspeccionesForm(data=request.POST, files=request.FILES)
      files = request.FILES.getlist('archivos')

      if formulario.is_valid():
         formulario.save()
         getid = formulario.save()
         getid.estado_actual='SOLICITADA'
         getid.save()

         # guardo datos en la tabla de estados
         estados.objects.create(
         referencia = 'INSPECCIÓN',
         identificador = getid.id,
         estado = getid.estado_actual ,   
         motivo = 'Inicio de la solicitud de Inspección.',
         )
         
         # guardo archivos en la tabla archivos         
         for f in files:
            archivos.objects.create(
               referencia = 'INSPECCIÓN',
               identificador = getid.id,
               archivo = f,
               nombre = f.name,
               tipo = f.content_type,
            )             

         messages.success(request, "Agregado correctamente.")
         return redirect(to='ver_inspeccion',id=getid.id)
      else:
         messages.error(request, "No se pudo agregar.")
         data["form"] = formulario
         
   data = {
      'form': InspeccionesForm(),
      'accion': 'Solicitar',
   }

   return render(request, 'modulo4/inspecciones/form_inspeccion.html', data)

def modificarInspeccion(request,id):  
   i=inspecciones.objects.filter(id=id).first()
   
   if request.method == 'POST':
      formulario = InspeccionesForm(instance = i,data=request.POST, files=request.FILES)
      files = request.FILES.getlist('archivos')

      if formulario.is_valid():
         formulario.save()
         getid = formulario.save()

         # guardo archivos en la tabla archivos         
         for f in files:
            archivos.objects.create(
               referencia = 'INSPECCIÓN',
               identificador = getid.id,
               archivo = f,
               nombre = f.name,
               tipo = f.content_type,
            )             

         messages.success(request, "Agregado correctamente.")
         return redirect(to='ver_inspeccion',id=getid.id)
      else:
         messages.error(request, "No se pudo agregar.")
         data["form"] = formulario
         
   data = {
      'form': InspeccionesForm(instance = i),
      'accion': 'Modificar',
   }
   return render(request, 'modulo4/inspecciones/form_inspeccion.html', data)

def buscarInspeccion(request):

   insp=inspecciones.objects.all()
   vis=visitas.objects.all()
   actas=actasDeInspeccion.objects.all()
   sedes = sedes_info.objects.all()


   if request.method == 'POST':
      q = request.POST
      print(q)
      for k,v in q.items(): 
         if v:
            if k =='sede': insp = insp.filter(sede__nombre = v)
            if k =='estado_inspeccion': insp = insp.filter(estado_actual = v)
            if k =='estado_visita':
               if v=='SIN VISITA':
                  insp = insp.exclude(estado_actual = 'ACEPTADA')
               else:
                  vis = vis.filter(estado_actual= v)
                  if vis:
                     for visita in vis:
                        insp = insp.filter(id = visita.id)
                  else: insp=None
      if insp:        
         messages.success(request, "Resultado de busqueda")
      else:
         messages.error(request, "No se encontraron resultados.") 
   
   data = { 
      'insp' :  insp,
      'vis':vis,
      'sedes':sedes,
      'actas':actas,
      'estado_visita':CHOICE_ESTADO_VISITA,
      'estado_inspeccion':CHOICE_ESTADO_INSPECCION,
      }
   return render(request,'modulo4/inspecciones/buscar_inspeccion.html', data)

#endregion-----------------------------------------


#region------------VIEW PROVEEDORES----------------------------
def listarProveedores(request):
   ots=ordenes_de_trabajo.objects.exclude(estado_actual='COTIZANDO')
   ps = proveedores.objects.all()
   info_p = {}

   for p in ps:
      o=ots.filter(proveedor_asignado=p.id)
      info_p[p] = {
         'ot_asignadas':o.count(),
         'ot_ejecutadas': o.filter(estado_actual = 'FINALIZADA').count(),
         'ot_ejecucion': o.filter(estado_actual = 'EN EJECUCIÓN').count(),
         'ot_retrasadas': o.filter(estado_actual = 'DEMORADA').count(),
         'presup_asignado':o.aggregate(total=Sum('presup_aprobado')),
         'presup_ejecutado':o.aggregate(total=Sum('presup_ejecutado')),
         'presup_en_ejecucion':o.aggregate(total=Sum('presup_en_ejecucion')),
         'presup_pendiente':o.aggregate(total=Sum('presup_aprobado')-Sum('presup_ejecutado')-Sum('presup_en_ejecucion')),
         'reprogramaciones':o.aggregate(total=Sum('reprogramaciones')),
         }

   

   data = { 
      'info_p' :  info_p,
      }
   return render(request,'modulo4/proveedores/listar_proveedores.html', data)


def modificarProveedor(request,id):
   p=proveedores.objects.get(id=id)

   data = { 
      'form':ProveedoresForm(instance= p) 
      }

   if request.method == 'POST':
      form = ProveedoresForm(instance=p,data=request.POST, files=request.FILES)
      files = request.FILES.getlist('archivos')
      if form.is_valid():
         get_p=form.save()
         
         # guardo archivos en la tabla archivos         
         for f in files:
            archivos.objects.create(
               referencia = 'PROVEEDOR',
               identificador = id,
               archivo = f,
               nombre = f.name,
               tipo = f.content_type,
            )              

         messages.success(request, "Modificado correctamente.")
         return redirect(to='ver_proveedor',id=id)
      else:
         messages.error(request, "No se pudo modificar.")         
         
   return render(request,'modulo4/proveedores/form_proveedor.html', data)


def agregarProveedor(request):
   
   data = { 
      'form':ProveedoresForm() 
      }

   if request.method == 'POST':
      form = ProveedoresForm(data=request.POST, files=request.FILES)
      files = request.FILES.getlist('archivos')
      if form.is_valid():
         get_p=form.save()

         # guardo archivos en la tabla archivos         
         for f in files:
            archivos.objects.create(
               referencia = 'PROVEEDOR',
               identificador = id,
               archivo = f,
               nombre = f.name,
               tipo = f.content_type,
            )             

         messages.success(request, "Agregado correctamente.")
         return redirect(to='ver_proveedor', id=get_p.id)
      else:
         messages.error(request, "No se pudo agregar.")         
         
   return render(request,'modulo4/proveedores/form_proveedor.html', data)


def verProveedor(request,id):
   ots=ordenes_de_trabajo.objects.filter(proveedor_asignado=id)
   p = proveedores.objects.get(id=id)
   pr_adjuntos=archivos.objects.filter(referencia='PROVEEDOR',identificador=id)

   data = { 
   'p':p, 
   'ots':ots,
   'pr_adjuntos':pr_adjuntos,
   }

   return render(request,'modulo4/proveedores/ver_proveedor.html', data)

#endregion


#region----------- VIEW CALENDARIO ----------------------------

def calendario(request):
   
   cap = capacitaciones.objects.all()   
   record = recordatorio.objects.all()
   anio = date.today().year

   data = {
      'post' : form_recordatorio(),
      'cap': cap,
      'anio' : anio,
      'record' : record,
      }

   if request.method == 'POST':
      formulario = form_recordatorio(data=request.POST)
      if 'recordatorio_borrar' in request.POST:
         id = request.POST.get('post_id')
         form = recordatorio.objects.get(id=id)
         form.delete()
         messages.success(request, "Borrado correctamente.")
         return redirect(to='calendario_M4')

      elif 'recordatorio_crear' in request.POST:
         if formulario.is_valid():
            formulario.save()
            messages.success(request, "Agregado correctamente.")
            return redirect(to='calendario_M4')
         else:
            messages.error(request, "No se pudo agregar.")
            return redirect(to='calendario_M4')
      
      elif 'editar_tarea' in request.POST:
         id_get = request.POST.get('id')
         tarea = get_object_or_404(recordatorio, id=id_get)
         form = form_recordatorio(request.POST or None, instance= tarea)
         if form.is_valid():
            form.save()
            messages.success(request, "Modificado correctamente.")
            return redirect(to='calendario_M4')
         else:
            messages.error(request, "No se pudo agregar.")
            return redirect(to='calendario_M4')

      else:
         messages.error(request, "Se produjo un error en calendario")
         return redirect(to='calendario_M4')

   return render(request,'modulo4/calendario/calendario.html', data)
#endregion


#region----------- VIEW RECORDATORIOS -------------------------
def recordatorios(request):

   tareas = recordatorio.objects.all().order_by('fecha')

   data = {
      'post':form_recordatorio(),
      'tareas': tareas,
   }

   if request.method == 'POST':

      if 'agregar_tarea' in request.POST:
         formulario = form_recordatorio(data=request.POST)
         if formulario.is_valid():
            formulario.save()
            messages.success(request, "Se agrego correctamente.")
            return redirect(to='listar_recordatorios')
         else:
            messages.error(request, "No se pudo agregar.")

      elif 'editar_tarea' in request.POST:
         id_get = request.POST.get('id')
         tarea = get_object_or_404(recordatorio, id=id_get)
         form = form_recordatorio(request.POST or None, instance= tarea)
         if form.is_valid():
            form.save()
            messages.success(request, "Modificado correctamente.")
            return redirect(to='listar_recordatorios')
         else:
            messages.error(request, "No se pudo agregar.")
            return redirect(to='listar_recordatorios')

      elif 'borrar_tarea' in request.POST:
         id = request.POST.get('post_id')
         form = recordatorio.objects.get(id=id)
         form.delete()
         messages.success(request, "Borrado correctamente.")
         return redirect(to='listar_recordatorios')

      else:
         messages.error(request, "Se produjo un error en recordatorios.")
         return redirect(to='listar_recordatorios')

   return render(request,'modulo4/calendario/listar_recordatorios.html', data)

def editarRecordatorio (request, id):
   
   cap = get_object_or_404(recordatorio, id=id)

   data = {
      'post': form_recordatorio(instance=cap),
      'cap' : cap,
   }
   if request.method == 'POST':
      formulario = form_recordatorio(data=request.POST, instance=cap)
      if formulario.is_valid():
         formulario.save()
         messages.success(request, "Modificado correctamente.")
         return redirect(to='calendario')
      else:
         data["form"] = formulario
         messages.error(request, "No se pudo modificar.")

   return render(request,'modulo4/calendario/editar_recordatorio.html', data)
#endregion


#region----------- VIEW ACTA DE INSPECCION ------------------------
def verActa(request,id):
   acta= actasDeInspeccion.objects.filter(id=id).first()
   v = visitas.objects.get(id=acta.visita.id)
      
   data = {
      'v':v,
      'acta':acta,
   }
   return render(request,'modulo4/inspecciones/ver_acta.html',data)

def agregarActa (request,id):
   v = visitas.objects.get(id=id)
      
   data = {
      'v':v,
      'form': ActaInspeccionForm(v),
      'accion': 'Crear',
   }

   if request.method == 'POST':
      form = ActaInspeccionForm(data=request.POST, files=request.FILES)
      files = request.FILES.getlist('archivos')
      if form.is_valid():
         form.save()

         # guardo archivos en la tabla archivos         
         for f in files:
            archivos.objects.create(
               referencia = 'VISITA',
               identificador = id,
               archivo = f,
               nombre = f.name,
               tipo = f.content_type,
            )
         # guardo datos en la tabla de estados
         estados.objects.create(
         referencia = 'VISITA',
         identificador = v.id,
         estado = 'FINALIZADA' ,   
         motivo = 'Creación del ACTA de Inspección.',
         )
         
         v.fecha_finalizacion = request.POST.get('fecha_acta') 
         v.estado_actual = 'FINALIZADA' 
         v.save()            

         messages.success(request, "Agregado correctamente.")
         return redirect(to='ver_inspeccion',id=v.inspeccion.id)
      else:
         messages.error(request, "No se pudo agregar.")       
      

   return render(request,'modulo4/inspecciones/form_acta.html',data)

#endregion


#region----------- VIEW COMUNICACIONES ------------------------

def Comunicaciones (request):
   nombres = None
      
   data = {
      'nombres': nombres,
   }

   if request.method == 'POST':

      names_id = request.POST.getlist('nombre')
      for n in names_id:
         name = ''
      
      subject = f'SIS: Comunicado Subject'
      msg = request.POST['msg']
      message = f'''Cuerpo del mensaje.

        {msg}
        
        Sistema Integral de Sedes. GOPA
        '''
      email = EmailMessage(subject, message, EMAIL_HOST_USER, bcc='')
      email.content_subtype = 'html'

      if request.FILES:
         file = request.FILES['file']
         email.attach(file.name, file.read(), file.content_type)

      if msg:
         email.send()
         messages.success(request, "Mensaje enviado correctamente.")
         return render(request,'modulo4/comunicaciones/comunicaciones.html',data)
      else:
         messages.error(request, "No se pudo mandar el mensaje.")
         return render(request,'modulo4/comunicaciones/comunicaciones.html',data)

   return render(request,'modulo4/comunicaciones/comunicaciones.html',data)

#endregion


#region ---------- VIEW CAPACITACIONES --------------------

def agregarCapacitacion(request):

   data = {
      'form': CapacitacionesForm(),
      'accion': 'Agregar',
   }

   if request.method == 'POST':
      formulario = CapacitacionesForm(data=request.POST, files=request.FILES)
      if formulario.is_valid():
         form= formulario.save()
         messages.success(request, "Agregado correctamente.")
         return redirect(to='capacitacion',id=form.id)
      else:
         messages.error(request, "No se pudo agregar.")
         data["form"] = formulario
         
   return render(request, 'modulo4/capacitaciones/form_capacitaciones.html', data)


def consultarCapacitacion (request, id):

   cap = get_object_or_404(capacitaciones, id=id)
   
   if request.method == 'POST':
      if 'borrar' in request.POST:
         cap.delete()
         messages.success(request, "Borrado correctamente.")
         return redirect(to='listar_capacitaciones')

   data = {
      'cap':cap,
      }

   return render(request, 'modulo4/capacitaciones/capacitacion.html',data)


def modificarCapacitacion(request, id):
   
   cap = get_object_or_404(capacitaciones, id=id)
   img = cap.imagen

   data = {
      'form': CapacitacionesForm(instance=cap),
      'img': img,
      'accion': 'Modificar',
   }
   
   
   if request.method == 'POST':
      formulario = CapacitacionesForm(data=request.POST, instance=cap, files=request.FILES)
      if formulario.is_valid():
         getid = formulario.save()
         messages.success(request, "Modificado correctamente.")
         return redirect(to='capacitacion', id=getid.id)
      else:
         data["form"] = formulario
         messages.error(request, "No se pudo modificar.")
   
   
   return render(request, 'modulo4/capacitaciones/form_capacitaciones.html', data)


def listarCapacitacion(request):
   cap_prox = capacitaciones.objects.filter(fecha__gte=datetime.now()).order_by('fecha','nombre')
   cap_pas = capacitaciones.objects.filter(fecha__lte=datetime.now()).order_by('fecha','nombre')
   
   data = {
      'proximas': cap_prox,
      'pasadas': cap_pas,
   }
   
   return render(request,'modulo4/capacitaciones/listar_capacitaciones.html', data)

#endregion


#region------------------VIEW DEV----------------------------------
def verUpdate(request,id):
   u=updatesDev.objects.filter(id=id).first()
   up_pedido_adjuntos = archivos.objects.filter(referencia='UP-PEDIDO', identificador=id)
   up_devolucion_adjuntos = archivos.objects.filter(referencia='UP-DEVOLUCIÓN', identificador=id)

   data={
      'u':u,
      'up_pedido_adjuntos':up_pedido_adjuntos,
      'up_devolucion_adjuntos':up_devolucion_adjuntos,
   }

   if request.method == 'POST':
      print(request.POST)
      if 'borrado' in request.POST:
         if u.estado=='CERRADO':
            messages.error(request, "No se puede modificar un pedido CERRADO.")
            return redirect(to='ver_update',id=id)
         else:
            objeto = request.POST.get('objeto_borrar')
            id_objeto = request.POST.get('id_objeto_borrar')

            if objeto =='pedido':
               if u.estado == 'ACEPTADA':
                  messages.warning(request, "No se puede borrar un pedido ACEPTADO")
               else:              
                  up_pedido_adjuntos.delete()
                  up_devolucion_adjuntos.delete()
                  u.delete()            
                  messages.success(request, "Borrado correctamente.")
                  return redirect(to='listar_updates')        
            
            elif objeto[:7] == 'archivo': #borrado de archivos
               ref = objeto[8:]
               archivos.objects.get(referencia = ref ,id = id_objeto).delete()
               messages.success(request, "Borrado correctamente.")

   return render(request,'modulo4/updates/ver_update.html', data)


def modificarUpdate(request,id):
   u=updatesDev.objects.filter(id=id).first()
   if u.estado=='CERRADO':
         messages.error(request, "No se puede modificar un pedido CERRADO.")
         return redirect(to='ver_update',id=id)
   else:
      data = { 
         'form':ModificarUpdateForm(instance= u) 
         }

      if request.method == 'POST':      
         form = ModificarUpdateForm(instance=u,data=request.POST, files=request.FILES)
         files = request.FILES.getlist('archivos')
         if form.is_valid():
            get_p=form.save()
            
            # guardo archivos en la tabla archivos         
            for f in files:
               archivos.objects.create(
                  referencia = 'UP-DEVOLUCIÓN',
                  identificador = id,
                  archivo = f,
                  nombre = f.name,
                  tipo = f.content_type,
               )    
            messages.success(request, "Modificado correctamente.")
            return redirect(to='ver_update',id=id)
         else:
            messages.error(request, "No se pudo modificar.")         
            
      return render(request,'modulo4/updates/modificar_update.html', data)


def agregarUpdate(request):
   
   data = { 
      'form':AgregarUpdateForm() 
      }

   if request.method == 'POST':
      form = AgregarUpdateForm(data=request.POST, files=request.FILES)
      files = request.FILES.getlist('archivos')
      if form.is_valid():
         get_u=form.save()
         get_u.estado='SOLICITADO'
         get_u.save()

         # guardo archivos en la tabla archivos         
         for f in files:
            archivos.objects.create(
               referencia = 'UP-PEDIDO',
               identificador = get_u.id,
               archivo = f,
               nombre = f.name,
               tipo = f.content_type,
            )             

         messages.success(request, "Agregado correctamente.")
         return redirect(to='listar_updates')
      else:
         messages.error(request, "No se pudo agregar.")         
         
   return render(request,'modulo4/updates/agregar_update.html', data)


def listarUpdates(request):
   u=updatesDev.objects.all()


   if request.method == 'POST':
      q = request.POST
      for k,v in q.items(): 
         if v:
            if k =='pedido': u = u.filter(tipo_pedido = v)
            if k =='relevado': u = u.filter(tipo_relevado = v)
            if k =='estado': u = u.filter(estado = v)
            
      if u:        
         messages.success(request, "Resultado de busqueda")
      else:
         messages.error(request, "No se encontraron resultados.") 
   
   data = { 
      'u' :  u,
      'tipo':CHOICE_TIPO_DEV,
      'estado_dev':CHOICE_ESTADO_DEV,
      }
   return render(request,'modulo4/updates/listar_updates.html', data)

#endregion

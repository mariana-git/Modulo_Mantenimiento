from .views import *
from django.urls import path

urlpatterns = [
    path('',index, name ='mod4_index'),

    
    #---------- LINKS SEDES -----------------
    path('agregar-sede/',agregarSede, name='agregar_sede_M4'),
    path('detalle-sede/<id>/',detalleSede, name='detalle_sede_M4'),
    path('listar-sedes/',listarSede, name='listar_sede_M4'),
    path('modificar-sedes/<id>/',modificarSede, name='modificar_sede_M4'),

    #---------- LINKS ESTADOS -----------------
    path('cambiar-estado/<int:id>/<origen>/',cambiarEstado, name='cambiar_estado'),

    #---------- LINKS TICKETS ------------
    path('listar-tickets/',listarTickets, name='listar_tickets'),
    path('agregar-ticket/',agregarTicket, name='agregar_ticket'),
    path('modificar-ticket/<id>/',modificarTicket, name='modificar_ticket'),
    path('ticket/<int:id>/',consultarTicket, name='ticket'),
    path('buscar-ticket/',buscarTicket, name='buscar_ticket'),
    
    #---------- LINKS VISOR DE IMAGENES ------------
    path('ver-imagenes/<id>/<ref>/',verImagenes, name='ver_imagenes'),
    
    #---------- LINKS ACTAS DE INSPECCION  ------------
    path('agregar-acta/<id>/',agregarActa, name='agregar_acta'),
    path('ver-acta/<id>/',verActa, name='ver_acta'),

    #---------- LINKS INSPECCIONES ------------
    path('listar-inspecciones/',listarInspecciones, name='listar_inspecciones'),
    path('agregar-inspeccion/',agregarInspeccion, name='agregar_inspeccion'),
    path('modificar-inspeccion/<id>/',modificarInspeccion, name='modificar_inspeccion'),
    path('ver-inspeccion/<id>/',verInspeccion, name='ver_inspeccion'),
    path('buscar-inspeccion/',buscarInspeccion, name='buscar_inspeccion'),

    #---------- LINK COTIZACIONES -----------------
    path('detalle_cotizacion/<int:id>',detalleCotizacion, name='detalle_cotizacion'),

    
    #---------- LINKS OT -----------------
    path('modificar-ot/<id>/',modificarOT, name='modificar_ot'),

    #---------- LINKS PROVEEDORES ------------
    path('agregar-proveedor/',agregarProveedor, name='agregar_proveedor'),
    path('modificar-proveedor/<id>',modificarProveedor, name='modificar_proveedor'),
    path('ver-proveedor/<id>',verProveedor, name='ver_proveedor'),
    path('listar-proveedores/',listarProveedores, name='listar_proveedores'),

    
    #---------- LINKS CAPACITACIONES  -----------------
    path('agregar-capacitacion/',agregarCapacitacion, name='agregar_capacitacion'),
    path('capacitacion/<id>/',consultarCapacitacion, name='capacitacion'),
    path('listar-capacitaciones/',listarCapacitacion, name='listar_capacitaciones'),
    path('modificar-capacitacion/<id>/',modificarCapacitacion, name='modificar_capacitacion'),
    

    #---------- LINKS COMUNICACIONES  -----------------
    path('comunicaciones/',Comunicaciones, name='comunicaciones_M4'),

    
     #---------- LINKS CALENDARIO  -----------------
    path('calendario/',calendario, name='calendario_M4'),
    path('editar-recordatorio/<id>/',editarRecordatorio, name='editar_recordatorio_M4'),
    path('listar_recordatorios/',recordatorios, name='listar_recordatorios'),
     

     #---------- LINKS DEV  -----------------
    path('agregar-update/',agregarUpdate, name='agregar_update'),
    path('listar_updates/',listarUpdates, name='listar_updates'),
    path('ver_update/<id>',verUpdate, name='ver_update'),
    path('modificar_update/<id>',modificarUpdate, name='modificar_update'),
]


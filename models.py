from django.db import models
from datetime import datetime

from django.urls import reverse

# Create your models here.


#region ---------TABLA COMPARTIDAS------------------------

class estados(models.Model):    
    usuario = models.CharField(max_length=100,null=True, blank=True, default='usuarioActual')
    referencia = models.CharField(max_length=100)
    identificador = models.PositiveIntegerField()
    estado = models.CharField(max_length=40)
    motivo = models.CharField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

class archivos(models.Model):
    usuario = models.CharField(max_length=100,null=True, blank=True, default='usuarioActual')
    referencia = models.CharField(max_length=100)
    identificador = models.PositiveIntegerField()
    archivo = models.FileField(upload_to=referencia, null=True, blank=True)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tipo']

class calificacion(models.Model):
    usuario =  models.CharField(max_length=100, default='usuario actual', null=True, blank=True)
    referencia = models.CharField(max_length=100)
    identificador = models.PositiveIntegerField()
    puntos = models.PositiveIntegerField(default=0, null=True, blank=True)
    fecha= models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
            ordering = ['fecha']
#endregion


#region ---------TABLA PROVEEDORES -------------------------

class proveedores(models.Model):
    nombre = models.CharField(max_length=250)
    calle = models.CharField(max_length=150, null=True, blank=True)
    altura = models.CharField(max_length=20, null=True, blank=True)
    telefono = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    barrio = models.CharField(max_length=100, null=True, blank=True)
    cp = models.CharField(max_length=10, null=True, blank=True)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    activo = models.BooleanField(default=True, null=True, blank=True)
    obs = models.CharField(max_length=500, null=True, blank=True)
    fecha_creado = models.DateTimeField(auto_now_add=True)
    fecha_modificado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.nombre)
    class Meta:
        ordering = ['nombre']
#endregion
   

#region ---------TABLA SEDES -------------------------

class sedes_info (models.Model):
    nombre = models.CharField(max_length=250, null=False)
    short_name = models.CharField(max_length=10, null=True, blank=True)
    comuna = models.IntegerField(null=True, blank=True)
    objeto = models.CharField(max_length=50, null=True, blank=True)
    calle = models.CharField(max_length=250, default='', null=True, blank=True)
    altura = models.IntegerField(null=True, blank=True)
    CP = models.CharField(max_length=10, default='', null=True, blank=True)
    telefono = models.CharField(max_length=500, null=True, blank=True)
    barrios = models.CharField(max_length=500, null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    portada = models.ImageField(upload_to="img_sedes", null=True, blank=True, default='portada.png')
    activa = models.CharField(max_length=2, default='Si', null=False)
    observaciones = models.CharField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return str(self.nombre)
    class Meta:
        ordering = ['short_name']
    
    def ubicacion(self):
        if self.calle and self.altura:
            ubic = self.calle + ' ' + str(self.altura)
        else: ubic='no registrada'
        return ubic
#endregion
    

#region ---------TABLAS TICKETS -----------------------------

class tickets(models.Model):
    usuario = models.CharField(max_length=100, default='usuarioActual',null=True, blank=True)
    fecha_alta = models.DateTimeField(default=datetime.now)  
    sede = models.ForeignKey(sedes_info,on_delete=models.PROTECT)  
    piso = models.CharField(max_length= 10, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)   
    trabajo_req = models.CharField(max_length=100) 
    categoria = models.CharField(max_length=100) 
    obs = models.CharField(max_length=500)
    prioridad = models.CharField(max_length=10)
    riesgo = models.CharField(max_length=10)
    seguridad = models.CharField(max_length=10)
    proveed_sugerido = models.ForeignKey(proveedores,on_delete=models.CASCADE, null=True, blank=True) 
    estado_actual = models.CharField(max_length=30, default='SOLICITADO', null=True, blank=True)
    fecha_creado = models.DateTimeField(auto_now_add=True)
    fecha_modificado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fecha_alta']

#endregion
 

#region ---------TABLA ORDENES DE TRABAJO --------------------

class ordenes_de_trabajo(models.Model):
    ticket = models.ForeignKey(tickets,on_delete=models.CASCADE)  
    estado_actual = models.CharField(max_length=30)
    proveedor_asignado = models.ForeignKey(proveedores, on_delete=models.CASCADE,null=True, blank=True)
    fecha_asignacion = models.DateTimeField(null=True, blank=True) 
    fecha_inicio = models.DateTimeField(null=True, blank=True)    
    fecha_fin_prevista = models.DateTimeField(null=True, blank=True)    
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    reprogramaciones = models.PositiveIntegerField(null=True, blank=True)
    presup_aprobado = models.DecimalField(max_digits=21, decimal_places=2, default=0.00,null=True, blank=True)
    presup_ejecutado = models.DecimalField(max_digits=21, decimal_places=2,default=0.00, null=True, blank=True)
    presup_en_ejecucion = models.DecimalField(max_digits=21, decimal_places=2,default=0.00, null=True, blank=True)
    activa = models.BooleanField(default=True, null=True, blank=True)
    fecha_creado = models.DateTimeField(auto_now_add=True)
    fecha_modificado = models.DateTimeField(auto_now=True)

    def presup_pendiente(self):
        if self.presup_aprobado:
            total = self.presup_aprobado - (self.presup_ejecutado + self.presup_en_ejecucion)
        else: total = None
        return total

    def fechas(self):
        
        if self.fecha_inicio and self.fecha_fin_prevista:  return True                
        return False
    
    def transcurridos(self):
        hoy = datetime.today().date()
        if self.fecha_inicio:
            delta= hoy - self.fecha_inicio.date()
            return delta.days
        else: return None
    
    def restantes(self):        
        hoy = datetime.today().date()
        if self.fecha_fin_prevista and self.fecha_fin_prevista.date() > hoy:
            delta =self.fecha_fin_prevista.date() - hoy
            return delta.days
        else: return None

    def demora(self):
        hoy = datetime.today().date()
        if self.fecha_fin_prevista and self.fecha_fin_prevista.date() < hoy:
            delta = hoy - self.fecha_fin_prevista.date()
            return delta.days
        else: return None
    
    class Meta:
        ordering = ['fecha_modificado']

    
    # def porcent_ejecutado(self):
    #     if self.presupuesto_aprobado == None:
    #         return 0            
    #     return float(self.presupuesto_ejecutado*100/self.presupuesto_aprobado)
#endregion


#region ---------TABLA COTIZACIONES ------------------------
class cotizaciones(models.Model):
    usuario = models.CharField(max_length=100, default='usuarioActual',null=True, blank=True)
    proveedor = models.ForeignKey(proveedores,on_delete=models.CASCADE) 
    ot = models.ForeignKey(ordenes_de_trabajo,on_delete=models.CASCADE)     
    estado_actual = models.CharField(max_length=30,default='ENVIADA',null=True, blank=True)    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    obs = models.CharField(max_length=500,null=True, blank=True)
    activa = models.BooleanField(default=True, null=True, blank=True)
    fecha_modificado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_solicitud']

#endregion


#region ---------TABLAS INSPECCIONES ----------------------

class inspecciones(models.Model):
    usuario = models.CharField(max_length=100, default='usuarioActual')
    sede = models.ForeignKey(sedes_info,on_delete=models.PROTECT)  
    piso = models.CharField(max_length= 10, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)   
    obs = models.CharField(max_length=500)
    estado_actual = models.CharField(max_length=100, null=True, blank=True)   
    fecha_creado = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_modificado = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creado']

class visitas(models.Model):
    usuario = models.CharField(max_length=100, default='usuarioActual')
    inspeccion = models.ForeignKey(inspecciones,on_delete=models.PROTECT)
    estado_actual = models.CharField(max_length=100, null=True, blank=True)   
    fecha_visita = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    fecha_creado = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_modificado = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creado']

class actasDeInspeccion(models.Model):
    usuario = models.CharField(max_length=100, default='usuarioActual')
    visita = models.ForeignKey(visitas,on_delete=models.PROTECT)
    fecha_acta = models.DateTimeField(default= datetime.today(), null=True, blank=True)
    numero = models.PositiveIntegerField()
    obs = models.CharField(max_length=1000)
    fecha_creado = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_modificado = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creado']

#endregion


#region ---------TABLA CAPACITACIONES ---------------------
class capacitaciones(models.Model):
    nombre = models.CharField(max_length=250)
    fecha = models.DateField()
    hora = models.CharField(max_length= 2, null=True, blank=True)
    minutos = models.CharField(max_length= 2, null=True, blank=True)
    lugar = models.CharField(max_length=250, null=True, blank=True)
    calle = models.CharField(max_length=250, null=True, blank=True)
    altura = models.PositiveSmallIntegerField(null=True, blank=True)
    telefono = models.IntegerField(null=True, blank=True)
    modo = models.CharField(max_length=15, null=True, blank=True)
    url = models.URLField(max_length=250, null=True, blank=True)
    observaciones = models.CharField (max_length= 500, null=True, blank=True)
    imagen = models.ImageField(upload_to="capacitaciones", null=True, blank=True)    
    invitados = models.CharField(max_length=1000, null=True, blank=True)
    activa = models.BooleanField(default=True)
    fecha_creado = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def ubicacion(self):
        ubic = self.calle + ' ' + self.altura
        return ubic
#endregion   


#region ---------TABLA RECORDATORIOS-------------------------
class recordatorio(models.Model):
    titulo = models.CharField(max_length=250, null=False, blank=False)
    fecha = models.DateField(null=False, blank=False)
    hora = models.CharField(max_length= 2, null=True, blank=True)
    minutos = models.CharField(max_length= 2, null=True, blank=True)
    detalles = models.CharField (max_length= 500, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    completo = models.BooleanField(default=False)
#endregion


#region ----------TABLAS COMUNICACIONES -----------------------
class comunicaciones(models.Model):
    user =  models.CharField(max_length=250, null=True, blank=True)
    msg =  models.CharField(max_length=500, null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to="comunicaciones", null=True, blank=True, default='sin archivo')
    invitados = models.CharField(max_length=250, null=True, blank=True)

#endregion


#region ----------TABLAS UPDATES DEV -----------------------
class updatesDev(models.Model):
    usuario =  models.CharField(max_length=100, null=True, blank=True)
    tipo_pedido =  models.CharField(max_length=100, null=False, blank=False)
    titulo = models.CharField (max_length= 200, null=True, blank=True)
    cuando = models.CharField (max_length= 500, null=True, blank=True)
    hace = models.CharField (max_length= 500, null=True, blank=True)
    deberia = models.CharField (max_length= 500, null=True, blank=True)
    tipo_relevado = models.CharField (max_length= 100, null=True, blank=True)
    estado = models.CharField (max_length= 100, null=True, blank=True)
    tiempo_estimado = models.PositiveIntegerField (null=True, blank=True)
    devolucion = models.CharField (max_length= 500, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

#endregion
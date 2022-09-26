
from django import forms
from .models import *
from .validators import MaxSizeFileValidator
from .choices import *


#---------- ESPECIALES PARA FORMS -----------------
class DateInput(forms.DateInput):
    input_type = 'date'



#region --------- FORMULARIO ESTADOS ------------------------

def estados_opciones(tipo):
    if tipo == 'TICKET': return CHOICE_ESTADO_TICKET
    elif tipo == 'OT': return CHOICE_ESTADO_OT
    elif tipo == 'COTIZACIÓN': return CHOICE_ESTADO_COTIZACION
    elif tipo == 'INSPECCIÓN': return CHOICE_ESTADO_INSPECCION
    elif tipo == 'VISITA': return CHOICE_ESTADO_VISITA
    else: return []
    
class EstadosForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True,}),required=False)
    fecha_finalizacion = forms.DateField(widget=forms.ClearableFileInput(attrs={'type': 'date'}),required=False,help_text='Fecha real de finalización')
    fecha_visita = forms.DateField(widget=forms.ClearableFileInput(attrs={'type': 'date'}),required=False,help_text='Fecha de la Visita')

    def __init__(self, tipo = '',*args, **kwargs):
        super(EstadosForm,self).__init__(*args, **kwargs)        
        self.fields['referencia'].initial = tipo
        self.fields['estado'] = forms.ChoiceField(choices=estados_opciones(tipo),help_text='Seleccione el nuevo estado')
        self.fields['motivo'].help_text='Describa el motivo'
        for key, field in self.fields.items():
            field.label = ""

    class Meta: 
            model = estados
            fields = '__all__'
            widgets = {
                'motivo' :  forms.Textarea(attrs={'rows':3}),
        }


#endregion

#region --------- FORMULARIO PROVEEDORES ------------------

class ProveedoresForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True,}),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = proveedores
        fields = '__all__'
        widgets = {
            'provincia' : forms.Select(choices=CHOICE_PROVINCIAS),
            'obs' :  forms.Textarea(attrs={'rows':2}),
            'calle': forms.TextInput(attrs={'placeholder':'Calle'}),
            'altura': forms.TextInput(attrs={'placeholder':'Altura'}),
        }
#endregion

#region --------- FORMULARIOS TICKETS ----------------------

class TicketsForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),required=False)
   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = tickets
        fields = '__all__'
        widgets = {
            'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
            'trabajo_req': forms.Select(choices=CHOICE_TIPO_TRABAJO),
            'categoria': forms.Select(choices=CHOICE_CATEGORIA),
            'obs' :  forms.Textarea(attrs={'rows':4}),
            'prioridad' : forms.Select(choices=CHOICE_IMPACTO),
            'riesgo': forms.Select(choices=CHOICE_IMPACTO),
            'seguridad': forms.Select(choices=CHOICE_IMPACTO),
            
        }


#endregion 

#region ----------FORMULARIOS COTIZACIONES-----------------
class CotizacionesForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True,}),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = cotizaciones
        fields = '__all__'
        widgets = {
            'obs' :  forms.Textarea(attrs={'rows':3}),
        }



#endregion

#region --------- FORMULARIOS ORDENES DE TRABAJO -----------
class OTForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True,}),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = ordenes_de_trabajo
        fields = ['fecha_inicio','presup_aprobado','presup_ejecutado','presup_en_ejecucion','fecha_fin_prevista']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
            'fecha_fin_prevista': forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
            'presup_aprobado': forms.NumberInput(),
            'presup_ejecutado': forms.NumberInput(),
            'presup_en_ejecucion': forms.NumberInput(),
        }

#endregion

#region --------- FORMULARIO CALIFICACION ----------
class CalificacionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = calificacion
        fields = '__all__'

#endregion --------- FORMULARIO CALIFICACION----------

#region --------- FORMULARIOS SEDES ------------------
class SedesForm (forms.ModelForm):
    
    portada = forms.ImageField(required=False, label="Foto portada", validators=[MaxSizeFileValidator(max_file_size=2)])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""

    class Meta: 
        model = sedes_info
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder':'campo obligatorio'}),
            'telefono': forms.NumberInput(),
            'calle' : forms.TextInput(attrs={'placeholder':'Calle'}),
            'altura' : forms.NumberInput(attrs={'placeholder':'Altura'}),
            'CP' : forms.TextInput(attrs={'placeholder':'Código Postal'}),
            'barrios' : forms.TextInput(),
            'comuna': forms.NumberInput(),
            'activa': forms.HiddenInput(attrs={'value': 'Si'}),
            'observaciones': forms.Textarea(attrs={'rows':3}),
        }

#endregion

#region --------- FORMULARIOS INSPECCIONES ----------------------

class InspeccionesForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = inspecciones
        fields = '__all__'
        widgets = {
            'obs' :  forms.Textarea(attrs={'rows':4}),
            
        }


#endregion 

#region --------- FORMULARIO ACTAS DE INSPECCION ------------------

class ActaInspeccionForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),required=False)

    def __init__(self,id='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
        if id: self.fields['visita'].initial = id
        
    
    class Meta: 
        model = actasDeInspeccion
        fields = '__all__'
        widgets = {
            'obs' :  forms.Textarea(attrs={'rows':5}),
            'numero': forms.NumberInput(),
            'fecha_acta': forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
        }
#endregion

#region --------- FORMULARIOS CAPACITACIONES -------------

class CapacitacionesForm(forms.ModelForm):
    
    imagen = forms.ImageField(required=False, label="", validators=[MaxSizeFileValidator(max_file_size=2)])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
        
    class Meta: 
        model = capacitaciones
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
            'hora': forms.Select(choices=CHOICE_HORA),
            'minutos': forms.Select(choices=CHOICE_MINUTOS),
            'calle' : forms.TextInput(attrs={'placeholder':'Calle'}),
            'altura' : forms.NumberInput(attrs={'placeholder':'Altura'}),
            'observaciones': forms.Textarea(attrs={'rows':3}),
            'url': forms.URLInput(),
            'modo': forms.Select(choices=CHOICE_MODO),
            
        }

#endregion    

#region --------- FORMULARIOS RECORDATORIOS -------------

class form_recordatorio(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""

    class Meta:
        model = recordatorio
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder':'campo obligatorio'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
            'hora': forms.Select(choices=CHOICE_HORA),
            'minutos': forms.Select(choices=CHOICE_MINUTOS),
            'detalles': forms.Textarea(attrs={'rows':3}),
            'color': forms.TextInput(),
        }
#endregion
       
#region --------- FORMULARIOS COMUNICACIONES -------------

class form_comunicaciones (forms.ModelForm):
    class Meta:
        model = comunicaciones
        fields = '__all__'
#endregion

#region --------- FORMULARIOS UPDATES DEV ----------------------

class AgregarUpdateForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = updatesDev
        fields = ['tipo_pedido','titulo','cuando','hace','deberia','usuario']
        widgets = {
            'tipo_pedido': forms.Select(choices=CHOICE_TIPO_DEV),
            'titulo':forms.TextInput(attrs={'placeholder':'   sintetice en una frase el requerimiento'}),
            'cuando':forms.Textarea(attrs={'rows':5,'placeholder':'   describa la acción que intenta realizar'}),
            'hace':forms.Textarea(attrs={'rows':5,'placeholder':'   describa la respuesta actual del sistema'}),
            'deberia':forms.Textarea(attrs={'rows':5,'placeholder':'   describa la acción que esperaba/espera recibir'}),
            # 'tipo_relevado': forms.Select(choices=CHOICE_TIPO_DEV),
            # 'tiempo_estimado':forms.NumberInput(),
            # 'estado': forms.Select(choices=CHOICE_ESTADO_DEV),
            # 'devolucion':forms.Textarea(attrs={'rows':5}),
            
        }
class ModificarUpdateForm(forms.ModelForm):

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""
    
    class Meta: 
        model = updatesDev
        fields = ['tipo_relevado','tiempo_estimado','estado','devolucion']
        widgets = {
            'tipo_relevado': forms.Select(choices=CHOICE_TIPO_DEV),
            'tiempo_estimado':forms.NumberInput(attrs={'placeholder':'   expresado en cantidad de días'}),
            'estado': forms.Select(choices=CHOICE_ESTADO_DEV),
            'devolucion':forms.Textarea(attrs={'rows':5,'placeholder':'   describa la solución a informar'}),
            
        }


#endregion 

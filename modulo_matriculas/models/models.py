import datetime

from odoo import fields, models, api
from odoo.exceptions import ValidationError



class Carrera(models.Model):
    _name = "ma.carrera"
    _description = "Carrera"
    name = fields.Char(string="Nombre de la Carrera", required=True)



class Matricula(models.Model):
    _name = "ma.matricula"
    _description = "Matricula"

    name = string="Matriculas"

    user_id = fields.Many2one(
        "res.users", string="Alumno",
        default=lambda self: self.env.uid,
        ondelete="cascade")

    periodo_id = fields.Many2one(
        "ma.periodomatricula", string="Periodo Matrícula",
        default=lambda self: self.env['ma.periodomatricula'].search([], limit=1),
        ondelete="cascade")

    tipo_matricula = fields.Selection(
        selection=[("segunda_matricula", "Segunda Matrícula"), ("tercera_matricula", "Tercera Matrícula")],
        string="Tipo de Matrícula", default="segunda_matricula", required=True)

    carrera_id = fields.Many2one(
        "ma.carrera", string="Carrera",
        default=lambda self: self.env['ma.carrera'].search([], limit=1),
        ondelete="cascade")

    ciclo_materias_reprobadas = fields.Many2one("ma.ciclo", string="Ciclo en el cual reprobó asignaturas")

    #Campo para Paralelo y validaciones
    paralelo_ciclo_reprobar = fields.Many2one("ma.paralelo", string="Paralelo del Ciclo en el cual reprobó asignaturas")

    asignaturas_reprobadas = fields.Many2many(
        'ma.asignatura', 'ma_asignaturarep_rel',
        'asignatura_id', 'ciclo_id', string='Asignaturas Reprobadas'
    )
    
    matricular_mismo_ciclo = fields.Boolean(string="Matricularse en el mismo ciclo?", default=False)

    ciclo_materias_matricular = fields.Many2one("ma.ciclo", string="Ciclo en el cual se va a matricular")

    asignaturas_matricular = fields.Many2many(
        'ma.asignatura', 'ma_asignaturamat_rel',
        'asignatura_id', 'ciclo_id', string='Asignaturas Matricular'
    )

    periodomatricula_id = fields.Many2one("ma.periodomatricula", string="Periodo Matrículas",
                                       default=lambda self: self.env['ma.periodomatricula'].search([], limit=1),
                                       ondelete="cascade")

    @api.onchange('asignaturas_reprobadas')
    def _modificarCiclos(self):
        self._materiasMatricula()
        contador = 0
        ciclo_reprobado = self.ciclo_materias_reprobadas
        numero_asignaturas = ciclo_reprobado.n_asignaturas
        n_materias_matricular = round(numero_asignaturas*0.40)
        tipo_matri = self.tipo_matricula
        for record in self.asignaturas_reprobadas:
            contador = contador + 1
        if contador > 1 and tipo_matri == "tercera_matricula":
            raise ValidationError("No puedes seleccionar mas de una materias")
        elif contador>n_materias_matricular and tipo_matri=="segunda_matricula":
            raise ValidationError("No puedes seleccionar mas del 40% de materias")

    @api.onchange('ciclo_materias_matricular')
    def _materiasMatriculaCicloRepetido(self):
        if self.ciclo_materias_matricular:
            if self.ciclo_materias_matricular.id == self.ciclo_materias_reprobadas.id:
                raise ValidationError ("Si desea seleccionar el mismo ciclo. Por favor marqué la casilla de matricular en el mismo ciclo")

    @api.onchange('asignaturas_matricular')
    def _materiasMatricula(self):

        creditos = self.ciclo_materias_matricular.creditos
        ciclo_matricular = self.ciclo_materias_matricular
        paralelo_anterior = self.paralelo_ciclo_reprobar
        creditos = round(creditos * 0.60)
        asignaturas_no = ""
        error_cadena = ""
        error_creditos = ""
        error_horario = []
        creditos_suma = 0

        paralelo_matricular = self.env['ma.paralelo'].search(
            [('name', '=', paralelo_anterior.name), ('ciclo_id', '=', ciclo_matricular.id)])
        print("Entra")
        print(paralelo_matricular.name)
        print(paralelo_matricular)
        print(ciclo_matricular.id)
        if paralelo_matricular.name == False:
            paralelo_matricular = self.env['ma.paralelo'].search(
                [('ciclo_id', '=', ciclo_matricular.id)], limit=1)

        print(paralelo_matricular.name)
        print(ciclo_matricular.id)
        for matricular in self.asignaturas_matricular:
            creditos_suma = creditos_suma + matricular.creditos
            for reprobadas in self.asignaturas_reprobadas:
                # Horario Inicio
                for pa_lunes in paralelo_anterior.horario_lunes:
                    for pm_lunes in paralelo_matricular.horario_lunes:
                        if pa_lunes.asignatura_id.id == reprobadas._origin.id and pa_lunes.numero_hora == pm_lunes.numero_hora \
                                and pm_lunes.asignatura_id.id == matricular._origin.id:
                            error_horario.append(pm_lunes.asignatura_id.name)
                for pa_martes in paralelo_anterior.horario_martes:
                    for pm_martes in paralelo_matricular.horario_martes:
                        if pa_martes.asignatura_id.id == reprobadas._origin.id and pa_martes.numero_hora == pm_martes.numero_hora \
                                and pm_martes.asignatura_id.id == matricular._origin.id:
                            error_horario.append(pm_martes.asignatura_id.name)
                for pa_miercoles in paralelo_anterior.horario_miercoles:
                    for pm_miercoles in paralelo_matricular.horario_miercoles:
                        if pa_miercoles.asignatura_id.id == reprobadas._origin.id and pa_miercoles.numero_hora == pm_miercoles.numero_hora \
                                and pm_miercoles.asignatura_id.id == matricular._origin.id:
                            error_horario.append(pm_miercoles.asignatura_id.name)
                for pa_jueves in paralelo_anterior.horario_jueves:
                    for pm_jueves in paralelo_matricular.horario_jueves:
                        if pa_jueves.asignatura_id.id == reprobadas._origin.id and pa_jueves.numero_hora == pm_jueves.numero_hora \
                                and pm_jueves.asignatura_id.id == matricular._origin.id:
                            error_horario.append(pm_jueves.asignatura_id.name)
                for pa_viernes in paralelo_anterior.horario_viernes:
                    for pm_viernes in paralelo_matricular.horario_viernes:
                        if pa_viernes.asignatura_id.id == reprobadas._origin.id and pa_viernes.numero_hora == pm_viernes.numero_hora \
                                and pm_viernes.asignatura_id.id == matricular._origin.id:
                            error_horario.append(pm_viernes.asignatura_id.name)
                # Horario Fin
                for prerre in matricular.prerrequisitos:
                    if prerre._origin.id == reprobadas._origin.id:
                        asignaturas_no = asignaturas_no + reprobadas.name + '; '
                        error_cadena = "Las siguientes asignaturas son cadena: "
        if creditos_suma > creditos:
           error_creditos = "Has superado el nivel de créditos u horas, selecciona nuevamente. \n" + \
                            "Puedes elegir " + str(creditos) + " Créditos u Horas"
        if error_cadena:
            raise ValidationError(error_cadena + asignaturas_no)
        elif error_creditos:
            raise ValidationError(error_creditos)
        elif error_horario:
            resultantList = []

            for element in error_horario:
                if element not in resultantList:
                    resultantList.append(element)
            raise ValidationError("No puede matricularse a las siguientes materias por temas de horarios: " + str(resultantList))

    def proceso_matricularse(self):

        periodos = self.env['ma.periodomatricula'].search([('estado', '=', True)])
        prerrequisito = self.env['ma.prerrequisito'].search([('user_id', '=', self.env.uid)])
        print("Entra")
        if prerrequisito:
            raise ValidationError("Usted ya cuenta con un proceso de matrícula iniciado")
        elif periodos:
            return {
                'name': 'Matriculación',
                'type': 'ir.actions.act_window',
                'res_model': 'ma.prerrequisito',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'self'
            }
        else:
            raise ValidationError("No puede matricularse porque no existen periodos para matrículas activos")


    def validarTiempoMatricula(self):
        periodos = self.env['ma.periodomatricula'].search([('estado', '=', True)])
        today = fields.Date.today()
        for periodo in periodos:
            if today >= periodo.fecha_fin:
                periodo.estado = False

    @api.model
    def create(self, vals):
        matricula = self.env['ma.matricula'].search([('user_id', '=', self.env.uid)], limit=1)
        if matricula:
            raise ValidationError("Usted solo puede crear una matrícula")
        else:
            return super(Matricula, self).create(vals)


class Prerrequisito(models.Model):
    _name = "ma.prerrequisito"
    _description = "Prerrequisitos de Matrícula"

    user_id = fields.Many2one(
        "res.users", string="Alumno",
        default=lambda self: self.env.uid,
        ondelete="cascade")

    documento_revisar_solicitud_decano = fields.Binary(string="Cargue la solicitud al decano")
    enviar_solicitud_decano = fields.Boolean(default=False, string="Estado de envío solicitud decano")
    aprobado_solicitud_decano = fields.Boolean(default=False, string="¿Solicitud decano aprobada?")
    documento_denegar_solicitud_decano = fields.Binary(
        string="Cargue el documento firmado con las razones por el cuál se nego la matrícula al estudiante")

    documento_revisar_asignacion_categoria = fields.Binary(string="Cargue documento de asignación de categoría")
    documento_revisar_solicitud_calculo_valores = fields.Binary(string="Cargue solicitud de cálculo de valores")
    enviar_solicitud_calculo_valores = fields.Boolean(default=False, string="Estado de envío solicitud de cálculo de valores")
    documento_aprobado_solicitud_calculo_valores = fields.Binary(
        string="Cargue la solicitud de cálculo de valores realizada")
    aprobado_solicitud_calculo_valores = fields.Boolean(default=False, string="¿Solicitud cálculo de valores aprobada?")

    documento_revisar_comprobante_pago = fields.Binary(string="Cargue comprobante de pago")
    aprobado_comprobante_pago = fields.Boolean(default=False, string="¿Comprobante de pago aprobado?")

    enviar_notificacion_comprobante = fields.Boolean(default=False, string="¿Notificación del envío de comprobante?")
    
    matricula_aprobada = fields.Boolean( string="Matrícula Aprobada")

    razon_no_comprobante = fields.Text(string="¿Por qué no se aprobó el comprobante?")

    fecha_inicio_proceso = fields.Date(string="Fecha de inicio", default=fields.Date.context_today)

    fecha_valores_secretaria = fields.Date(string="Fecha envío de solicitud Valores Secretaria", default=fields.Date.context_today)
    fecha_comprobante_secretaria = fields.Date(string="Fecha envío de Comprobante de pago Secretaria", default=fields.Date.context_today)
    fecha_cumplir_requisito = fields.Date(string="Fecha cumplir requisitos", default=fields.Date.context_today)

    def enviar_decano(self):
        if self.documento_revisar_solicitud_decano:
            grupo_decano = self.env['res.groups'].search([('name', '=', 'Decano')])
            usuarios = self.env["res.users"].search([('groups_id', "=", grupo_decano.id)])
            for us in usuarios:
                try:
                    template_rec = self.env.ref('modulo_matriculas.email_template_envio_solicitud_decano')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(self.id, force_send=True)
                    self.enviar_solicitud_decano = True
                    self.fecha_inicio_proceso = fields.Date.today()
                except NameError:
                    raise ValidationError("Se produjo un error al envío de notificación.")
        else:
            raise ValidationError("Complete los campos requeridos")

    def enviar_secretaria(self):
        if self.documento_revisar_asignacion_categoria and self.documento_revisar_solicitud_calculo_valores:
            print("Entra")
            grupo_secretaria = self.env['res.groups'].search([('name', '=', 'Secretaria')])
            usuarios = self.env["res.users"].search([('groups_id', "=", grupo_secretaria.id)])
            for us in usuarios:
                try:
                    template_rec = self.env.ref('modulo_matriculas.email_template_envio_solicitud_secretaria')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(self.id, force_send=True)
                    self.enviar_solicitud_calculo_valores = True
                    self.fecha_valores_secretaria =  fields.Date.today()
                except NameError:
                    raise ValidationError("Se produjo un error al envío de notificación.")
        else:
            raise ValidationError("Complete los campos requeridos")

    @api.constrains('aprobado_solicitud_decano')
    def _notificarAprobacionDecano(self):
        if self.aprobado_solicitud_decano == True:
            grupo_secretaria = self.env['res.groups'].search([('name', '=', 'Secretaria')])
            usuarios = self.env["res.users"].search([('groups_id', "=", grupo_secretaria.id)])
            for us in usuarios:
                try:
                    template_rec = self.env.ref('modulo_matriculas.email_template_notificar_secretaria_decano')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(self.id, force_send=True)

                    template_rec = self.env.ref('modulo_matriculas.email_template_notificar_alumno_decano')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': self.user_id.login})
                    template_rec.send_mail(self.id, force_send=True)

                except NameError:
                    raise ValidationError("Se produjo un error al envío de notificación.")


    def enviar_comprobante(self):
        if self.documento_revisar_comprobante_pago:
            print("Entra")
            grupo_secretaria = self.env['res.groups'].search([('name', '=', 'Secretaria')])
            usuarios = self.env["res.users"].search([('groups_id', "=", grupo_secretaria.id)])
            for us in usuarios:
                try:
                    template_rec = self.env.ref('modulo_matriculas.email_template_notificar_alumno_secretaria_comprobante')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(self.id, force_send=True)
                    self.enviar_notificacion_comprobante = True
                    self.fecha_comprobante_secretaria = fields.Date.today()
                except NameError:
                    raise ValidationError("Se produjo un error al envío de notificación.")
        else:
            raise ValidationError("Complete los campos requeridos")


    @api.constrains('aprobado_comprobante_pago','razon_no_comprobante')
    def _notificarAprobacionFinal(self):
        print("Entra notificar")
        print(self.aprobado_comprobante_pago)
        print(bool(self.razon_no_comprobante))
        print(bool(self.razon_no_comprobante)==False)
        print(bool(self.razon_no_comprobante)==True)
        if self.aprobado_comprobante_pago and bool(self.razon_no_comprobante) == False:
            print("Entra condiciones")
            grupo_gestor = self.env['res.groups'].search([('name', '=', 'Gestor Academico')])
            print(grupo_gestor)
            usuarios = self.env["res.users"].search([('groups_id', "=", grupo_gestor.id)])
            print(usuarios)
            for us in usuarios:
                print(us)
                try:
                    template_rec = self.env.ref('modulo_matriculas.email_template_notificar_secretaria_gestor_aprueba')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(self.id, force_send=True)
                    self.fecha_cumplir_requisito = fields.Date.today()

                    template_rec = self.env.ref('modulo_matriculas.email_template_notificar_secretaria_alumno_comprobante')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': self.user_id.login})
                    template_rec.send_mail(self.id, force_send=True)

                except NameError:
                    raise ValidationError("Se produjo un error al envío de notificación.")

        elif bool(self.razon_no_comprobante) and self.aprobado_comprobante_pago == False \
                and self.enviar_notificacion_comprobante:
            try:
                template_rec = self.env.ref(
                        'modulo_matriculas.email_template_notificar_negacion_secretaria_alumno_comprobante')
                template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                template_rec.write({'email_to': self.user_id.login})
                template_rec.send_mail(self.id, force_send=True)
                self.enviar_notificacion_comprobante = False
            except NameError:
                raise ValidationError("Se produjo un error al envío de notificación.")


    @api.constrains('documento_aprobado_solicitud_calculo_valores','aprobado_solicitud_calculo_valores')
    def _notificarCalculoValores(self):
        if self.aprobado_solicitud_calculo_valores and self.documento_aprobado_solicitud_calculo_valores:
            try:
                template_rec = self.env.ref(
                        'modulo_matriculas.email_template_notificar_secretaria_alumno_calculo')
                template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                template_rec.write({'email_to': self.user_id.login})
                template_rec.send_mail(self.id, force_send=True)
            except NameError:
                raise ValidationError("Se produjo un error al envío de notificación.")
        elif self.aprobado_solicitud_calculo_valores==False and self.documento_aprobado_solicitud_calculo_valores:
            try:
                template_rec = self.env.ref(
                        'modulo_matriculas.email_template_notificar_negacion_secretaria_alumno_valores')
                template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                template_rec.write({'email_to': self.user_id.login})
                template_rec.send_mail(self.id, force_send=True)
                self.enviar_solicitud_calculo_valores=False
            except NameError:
                raise ValidationError("Se produjo un error al envío de notificación.")
        if self.aprobado_solicitud_calculo_valores and self.documento_aprobado_solicitud_calculo_valores==False:
            raise ValidationError("Porfavor cargue la respuesta a la petición")

    def validarMatricula(self):
        return {
            'name': 'Confirmar Matrícula',
            'type': 'ir.actions.act_window',
            'res_model': 'ma.confirmar_matricula',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            "context": {"id_matricula": self.id}
        }

    @api.constrains('documento_denegar_solicitud_decano')
    def _notificarNoSolicitudDecano(self):
        if self.documento_denegar_solicitud_decano and self.aprobado_solicitud_decano==False:
            try:
                template_rec = self.env.ref(
                    'modulo_matriculas.email_template_negacion_solicitud_alumno_decano')
                template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                template_rec.write({'email_to': self.user_id.login})
                template_rec.send_mail(self.id, force_send=True)
                self.enviar_solicitud_decano = False
            except NameError:
                raise ValidationError("Se produjo un error al envío de notificación.")

    def recordarDecano(self):
        matriculas = self.env['ma.prerrequisito'].search([('aprobado_solicitud_decano', '=', False)])
        today = fields.Date.today()
        for matricula in matriculas:
            aux = matricula.fecha_inicio_proceso + datetime.timedelta(days=1)
            if today == aux:
                grupo_decano = self.env['res.groups'].search([('name', '=', 'Decano')])
                usuarios = self.env["res.users"].search([('groups_id', "=", grupo_decano.id)])
                for us in usuarios:
                    template_rec = self.env.ref('modulo_matriculas.email_template_reenvio_solicitud_decano')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(matricula.id, force_send=True)

    def recordarSecretaria(self):
        matriculas = self.env['ma.prerrequisito'].search([('aprobado_solicitud_calculo_valores', '=', False)])
        today = fields.Date.today()
        for matricula in matriculas:
            aux = matricula.fecha_valores_secretaria + datetime.timedelta(days=1)
            if today == aux:
                grupo_secretaria = self.env['res.groups'].search([('name', '=', 'Secretaria')])
                usuarios = self.env["res.users"].search([('groups_id', "=", grupo_secretaria.id)])
                for us in usuarios:
                    template_rec = self.env.ref('modulo_matriculas.email_template_reenvio_solicitud_secretaria')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(matricula.id, force_send=True)

    def recordarSecretariaComprobante(self):
        matriculas = self.env['ma.prerrequisito'].search([('aprobado_solicitud_calculo_valores', '=', False)])
        today = fields.Date.today()
        for matricula in matriculas:
            aux = matricula.fecha_comprobante_secretaria + datetime.timedelta(days=1)
            if today == aux:
                grupo_secretaria = self.env['res.groups'].search([('name', '=', 'Secretaria')])
                usuarios = self.env["res.users"].search([('groups_id', "=", grupo_secretaria.id)])
                for us in usuarios:
                    template_rec = self.env.ref('modulo_matriculas.email_template_renotificar_alumno_secretaria_comprobante')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(matricula.id, force_send=True)

    def recordarGestorMatricula(self):

        matriculas = self.env['ma.prerrequisito'].search([('aprobado_solicitud_calculo_valores', '=', False)])
        today = fields.Date.today()
        for matricula in matriculas:
            aux = matricula.fecha_cumplir_requisito + datetime.timedelta(days=1)
            if today == aux:
                grupo_gestor = self.env['res.groups'].search([('name', '=', 'Gestor Academico')])
                usuarios = self.env["res.users"].search([('groups_id', "=", grupo_gestor.id)])
                for us in usuarios:
                    template_rec = self.env.ref('modulo_matriculas.email_template_renotificar_secretaria_gestor_aprueba')
                    template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
                    template_rec.write({'email_to': us.email})
                    template_rec.send_mail(self.id, force_send=True)


class Asignatura(models.Model):
    _name = "ma.asignatura"
    _description = "Asignaturas"

    name = fields.Char(string="Nombre de la asignatura", required=True)
    creditos = fields.Integer(string="Créditos/Horas")

    carrera_id = fields.Many2one(
        "ma.carrera", string="Carrera",
        default=lambda self: self.env['ma.carrera'].search([], limit=1),
        ondelete="cascade")

    ciclo_id = fields.Many2one("ma.ciclo", string="Ciclo")


    prerrequisitos = fields.Many2many(
        'ma.asignatura', 'ma_asignaturapre_rel',
        'asignatura_id', 'ciclo_id', string='Prerrequisitos'
    )

    @api.model
    def create(self, vals):
        usuario = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1)
        if usuario.has_group('modulo_matriculas.res_groups_alumnos'):
            raise ValidationError("Usted no puede crear Asignaturas")
        else:
            return super(Asignatura, self).create(vals)

    @api.constrains('ciclo_id')
    def _validarNMaterias(self):
        asignaturas = self.env['ma.asignatura'].search([('ciclo_id', '=', self.ciclo_id.id)])
        if len(asignaturas) > self.ciclo_id.n_asignaturas:
            raise ValidationError("Ha excedido el número de materias en el ciclo, por favor modificar número de materias en: \nDatos Carrera >> Ciclo")

    @api.constrains('ciclo_id', 'creditos')
    def _validarNCreditos(self):
        asignaturas = self.env['ma.asignatura'].search([('ciclo_id', '=', self.ciclo_id.id)])
        creditos = 0
        for asignatura in asignaturas:
            creditos = creditos + asignatura.creditos
        if creditos > self.ciclo_id.creditos:
            raise ValidationError(
                "Ha excedido el número de créditos en el ciclo, por favor modificar número de créditos en: \nDatos Carrera >> Ciclo")


class Periodomatricula(models.Model):
    _name = "ma.periodomatricula"
    _description = "Periódo de Matrículas"

    _sql_constraints = [
        ('name_unique', 'unique (name)',
         "El nombre del Periodo ya existe!"),
    ]

    name = fields.Char(string="Nombre del Periodo de Matrículas")
    fecha_inicio = fields.Date(string="Fecha de inicio")
    fecha_fin = fields.Date(string="Fecha de fin")
    estado = fields.Boolean(string ="Estado", default=True)

    matricula_ids = fields.One2many("ma.matricula", "periodomatricula_id",
                                       string="Matrículas",
                                       ondelete="cascade")

    def botonmatricularse(self):
        return {
                'name': 'Matriculas',
                'type': 'ir.actions.act_window',
                'res_model': 'ma.matricula',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'self'
            }
    
    @api.constrains('fecha_inicio')
    def _validarEstadoMatricula_inicio(self):
        today = fields.Date.today()
        if self.fecha_inicio <= today:
            self.estado = True
        else:
            self.estado = False

    @api.constrains('fecha_fin')
    def _validarEstadoMatricula_fin(self):
        today = fields.Date.today()
        if self.fecha_fin <= today:
            self.estado = False
        else:
            self.estado = True

    def validarInicioMatricula(self):
        periodos = self.env['ma.periodomatricula'].search([('estado', '=', False)])
        today = fields.Date.today()
        for periodo in periodos:
            if today >= periodo.fecha_inicio:
                periodo.estado = True


class Ciclo(models.Model):
    _name = "ma.ciclo"
    _description = " Ciclos"
    _sql_constraints = [
        ('name_unique', 'unique (name)',
         "El nombre del ciclo ya existe!"),
    ]

    name = fields.Char(string="Nombre del ciclo")
    nombre_ciclo = fields.Char(string="Nombre del ciclo", required=True)
    creditos = fields.Integer(string="Créditos")
    n_asignaturas = fields.Integer(string="Número de Asignaturas")
    numero_ciclo = fields.Selection(
        selection=[("ciclo_1", "1"), ("ciclo_2", "2"), ("ciclo_3", "3"),
                   ("ciclo_4", "4"), ("ciclo_5", "5"), ("ciclo_6", "6"),
                   ("ciclo_7", "7"), ("ciclo_8", "8"), ("ciclo_9", "9"), ("ciclo_10", "10")],
        string="Ciclo", required=True)
    carrera_id = fields.Many2one("ma.carrera", string="Carrera")

    paralelo_ids = fields.One2many("ma.paralelo", "ciclo_id",
                                    string="Paralelos")

    @api.constrains('nombre_ciclo')
    def crearNombre(self):
        nombre_ciclo = self.nombre_ciclo
        numero_ciclo = self.numero_ciclo
        self.name = str(numero_ciclo)[6 : ] + "." + str(nombre_ciclo)


class Paralelo(models.Model):
    _name = "ma.paralelo"
    _description = " Paralelos"

    name = fields.Char(string="Paralelo")
    horario_lunes = fields.One2many("ma.horario", "paralelo_id1",
                                    string="Lunes")
    horario_martes = fields.One2many("ma.horario", "paralelo_id2",
                                    string="Martes")
    horario_miercoles = fields.One2many("ma.horario", "paralelo_id3",
                                    string="Miércoles")
    horario_jueves = fields.One2many("ma.horario", "paralelo_id4",
                                    string="Jueves")
    horario_viernes = fields.One2many("ma.horario", "paralelo_id5",
                                    string="Viernes")

    carrera_id = fields.Many2one(
        "ma.carrera", string="Carrera",
        default=lambda self: self.env['ma.carrera'].search([], limit=1),
        ondelete="cascade")

    ciclo_id = fields.Many2one("ma.ciclo", string="Ciclo",
                                          default=lambda self: self._origin.id,
                                          ondelete="cascade")

class Horario(models.Model):
    _name = "ma.horario"
    _description = " Horario"

    numero_hora=fields.Selection(
        selection=[("1", "1ra"), ("2", "2da"), ("3", "3ra"),
                   ("4", "4ta"), ("5", "5ta"), ("6", "6ta"),
                   ("7", "7ma"), ("8", "8va"), ("9", "9na"), ("10", "10ma")], string="Número de Hora", required=True)

    asignatura_id = fields.Many2one(
        "ma.asignatura", string="Asignatura")


    paralelo_id1 = fields.Many2one("ma.paralelo", string="Paralelo",
                                          default=lambda self: self._origin.id,
                                          ondelete="cascade")
    paralelo_id2 = fields.Many2one("ma.paralelo", string="Paralelo",
                                  default=lambda self: self._origin.id,
                                  ondelete="cascade")
    paralelo_id3 = fields.Many2one("ma.paralelo", string="Paralelo",
                                  default=lambda self: self._origin.id,
                                  ondelete="cascade")
    paralelo_id4 = fields.Many2one("ma.paralelo", string="Paralelo",
                                  default=lambda self: self._origin.id,
                                  ondelete="cascade")
    paralelo_id5 = fields.Many2one("ma.paralelo", string="Paralelo",
                                  default=lambda self: self._origin.id,
                                  ondelete="cascade")

    carrera_id = fields.Many2one("ma.carrera", string="Carrera",
                               ondelete="cascade")
    ciclo_id = fields.Many2one("ma.ciclo", string="Ciclo",
                                  ondelete="cascade")
    
    

class confirmarMatricula(models.TransientModel):
    _name = 'ma.confirmar_matricula'

    yes_no = fields.Char(
        default='¿Desea confirmar la matrícula?')

    def yes(self):
        print("Entra metodo")
        id_matricula = self.env.context.get('id_matricula')
        print(id_matricula)
        matricula = self.env["ma.prerrequisito"].search([('id','=',id_matricula)])
        print(matricula)
        print("Entrar")
        matricula.write({'matricula_aprobada': True})
        print("Matriculado")

        try:
            self.env.cr.commit()
            template_rec = self.env.ref('modulo_matriculas.email_template_notificar_gestor_alumno_aprobacion')
            print("Envia mensaje")
            template_rec.write({'email_from': 'modulomatriculas@gmail.com'})
            print("Envia mensaje correo 1")
            template_rec.write({'email_to': matricula.user_id.login})
            print("Envia mensaje correo 2")
            template_rec.send_mail(matricula.id, force_send=True)
            print("Envia mensaje correo 3")
        except NameError:
            raise ValidationError("Se produjo un error al envío de notificación.")

class ResUser(models.Model):
    _inherit = "res.users"


    @api.constrains('vat')
    def _validarCedula(self):

        try:
            nocero = self.vat.strip("0")
            cedula = int(nocero, 0)
        except:
            raise ValidationError("Verifique el número de cédula")
        # sin ceros a la izquierda


        verificador = cedula % 10
        numero = cedula // 10

        # mientras tenga números
        suma = 0
        while (numero > 0):

            # posición impar
            posimpar = numero % 10
            numero = numero // 10
            posimpar = 2 * posimpar
            if (posimpar > 9):
                posimpar = posimpar - 9

            # posición par
            pospar = numero % 10
            numero = numero // 10

            suma = suma + posimpar + pospar

        decenasup = suma // 10 + 1
        calculado = decenasup * 10 - suma
        if (calculado >= 10):
            calculado = calculado - 10

        if (calculado != verificador):
            raise ValidationError("Verifique el número de cédula")

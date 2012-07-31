from actions import *
from billing.models import *
from common.utils.response import download_files
from contacts.service_support.views import select_contact_view
from contacts.models import Contact
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from forms import BillLineForm, AmendedBillLineForm, get_bill_form, get_bill_change_link
import settings


def bill_link(self):
    return get_bill_change_link(self.bill)
bill_link.short_description = _("Bill")
bill_link.allow_tags = True


class BillLineTabularInline(admin.TabularInline):
    model = BillLine
    extra = 0
    max_num = 0
    can_delete = False
    fields = ['line_number','order_id','description','initial_date','final_date','price','amount','tax'] 
    form = BillLineForm


class BudgetLineTabularInline(admin.TabularInline):
    model = BudgetLine


class AmendedBillLineTabularInline(BillLineTabularInline):
    fields = ['line_number','order_id','description','initial_date','final_date','price','amount','tax','amended_bill'] 
    form = AmendedBillLineForm


def budget_link(self):
    url = reverse('admin:billing_budget_change', args=(self.id,))
    return '<a href="%(url)s">%(budget_id)s</a>' % {'url': url, 'budget_id': self.budget.ident}
budget_link.short_description=_("Budget")
budget_link.allow_tags=True


def amended_bill(self):
    try: a_bill = self.subclass_instance.amended_line.bill
    except self.DoesNotExist: return ''
    else:
        a_bill_type = a_bill.__class__.__name__.lower()
        url = reverse('admin:billing_%s_change' % (a_bill_type), args=(a_bill.id,))
        return '<a href="%s">%s</a>:%s' % (url, a_bill.ident, self.subclass_instance.amended_line.line_number)
amended_bill.short_description = _("Amended Bill")
amended_bill.allow_tags = True


class ManageBillLineAdmin(admin.ModelAdmin):
    actions = (manual_amend_line, auto_amend_total_value, move_lines, delete_lines,)      
    change_list_template = 'admin/billing/billline/manage_bill_line_change_list.html'
    
    def __init__(self, *args, **kwargs):
        model = args[0]
        if model is BillLine:
            #TODO: proivide order link to order_id field        
            self.list_display = ('line_number', 'order_id', 'description', 'initial_date', 'final_date', 'price', 'amount', 'tax', bill_link, amended_bill)
            self.fieldsets = ((None,     {'fields': (('description'),
                                                    ('initial_date'),
                                                    ('final_date'),
                                                    ('amount'),
                                                    ('price'),
                                                    ('tax'),)}),)    
        else: 
            self.list_display = ('description', 'initial_date', 'final_date', 'price', 'amount', 'tax', budget_link )
            self.fieldsets = ((None,     {'fields': (('description'),
                                                    ('initial_date'),
                                                    ('final_date'),
                                                    ('amount'),
                                                    ('price'),
                                                    ('tax'),)}),)       
        super(ManageBillLineAdmin, self).__init__(*args, **kwargs)             
        
    def get_bill(self, request):
        bill_id = request.META['PATH_INFO'].split('/manage_lines/')[0].split('/')[-1]    
        bill_cls = get_bill_class(self.model)
        return bill_cls.objects.get(id=bill_id)
        
    def get_actions(self, request):
        actions = super(ManageBillLineAdmin, self).get_actions(request)
        del actions['delete_selected']
        if self.get_bill(request).status == settings.OPEN:
            del actions['manual_amend_line']
            del actions['auto_amend_total_value']
        else:
            del actions['move_lines']
            del actions['delete_lines']
            if self.model is BudgetLine:
                del actions['manual_amend_line']
                del actions['auto_amend_total_value']
        return actions
    
    def get_urls(self):
        """Returns the additional urls used by the Contact admin."""
        urls = super(ManageBillLineAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name,
        if self.model in (InvoiceLine, AmendedInvoiceLine): am_cls = AmendedInvoiceLine
        elif self.model in (FeeLine, AmendedFeeLine): am_cls = AmendedFeeLine
        # Just for avoiding errors 
        else: am_cls = BudgetLine
            
        contact_urls = patterns("",
            url("move/$", admin_site.admin_view(self.move_lines_view), name='billing_billline_move'),
            url("add_amended/(?P<bill_line_id>\d+)/$", ManageBillLineAdmin(am_cls, admin_site).amend_add_view, name='billing_billine_add_admend'),)
#            url("merda/$", ManageBillLineAdmin(am_cls, admin_site).amend_add_view, name='billing_amendedinvoiceline_changelist'),)
        return contact_urls + urls 

    @method_decorator(csrf_protect)
    @transaction.commit_on_success
    def amend_add_view(self, request, object_id, bill_line_id, form_url='', extra_context=None): 
        #TODO: provide and inline with the original line.
        from django.utils.encoding import force_unicode
        from django.core.exceptions import PermissionDenied
        model = self.model
        opts = model._meta
        bill_line = BillLine.objects.get(pk=bill_line_id)
        bill = bill_line.bill
        
        if not super(ManageBillLineAdmin, self).has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                line = self.save_form(request, form, change=False)
                line.order_id=bill_line.order_id
                line.amended_line_id = bill_line_id
                bills = Bill.create(bill.contact, [line])
                self.log_addition(request, line)
                msg = _('The %(name)s "%(obj)s" was added successfully.') %  {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(line)}
                self.message_user(request, msg)
                return HttpResponseRedirect('../../')
            else:
                form_validated = False
                new_object = self.model()
            prefixes = {}
            
        else:
            initial = dict(request.GET.items())
            form = ModelForm(initial=initial)
            prefixes = {}

        adminForm = admin.helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        context = {
            'title': _('Create %s for %s:%s') % (force_unicode(opts.verbose_name),bill.ident, bill_line.line_number),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': mark_safe(media),
#            'inline_admin_formsets': inline_admin_formsets,
            'errors': admin.helpers.AdminErrorList(form, []),
            'app_label': opts.app_label,
#            'has_change_permission': False,
        }

        context.update(extra_context or {})
        #from django.shortcuts import render_to_response
        self.change_list_template = 'admin/billing/billline/select_bill.html'	
        return self.render_change_form(request, context, form_url=form_url, add=True)
#        return render_to_response("admin/billing/billline/add_amendline.html", context) 
   
    def has_add_permission(self, request):
        """ Disable add link when bill is close"""
        bill = self.get_bill(request)
        if bill.status == settings.OPEN:
            if isinstance(bill, Bill) and isinstance(bill.subclass_instance, (Invoice, Fee)):
                return super(ManageBillLineAdmin, self).has_add_permission(request)
        return False
                                       
    @transaction.commit_on_success                                                                     
    def move_lines_view(self, request, object_id): 
        """ """
        bill_id = request.GET['bill_id']
        bill_lines = map(lambda(x): int(x), request.GET['bill_lines'].split(','))
        bill_lines = self.model.objects.filter(id__in=bill_lines)
        for bill_line in bill_lines:
            bill_line.bill_id=bill_id
            bill_line.save()
        bill_cls = get_bill_class(self.model)
        bill_cls_lower = bill_cls.__name__.lower()
        url = "/admin/billing/%s/%s/manage_lines" % (bill_cls_lower, object_id)
        self.message_user(request, "Lines Succesfully moved")
        return HttpResponseRedirect(url)

    def changelist_view(self, request, extra_context=None):
        bill_cls = get_bill_class(self.model)
        bill_cls_lower = bill_cls.__name__.lower()
        bill = extra_context['bill']
        # Filter BillLines related to the current bill
        q = request.GET.copy()
        q[bill_cls_lower] = bill.pk
        request.GET = q
        request.META['QUERY_STRING'] = request.GET.urlencode()
        bill_subtype = bill.__class__.__name__.lower()
        context = { 'bill_type': bill_cls_lower, 'bill_subtype': bill_subtype}
        context.update(extra_context or {})
        return super(ManageBillLineAdmin,self).changelist_view(request, extra_context=context)    
        
    def add_view(self, request, object_id, form_url='', extra_context=None):
        bill_cls = get_bill_class(self.model)
        ident = bill_cls.objects.get(pk=object_id).ident
        context = {'title': 'Add %s to %s' % (self.model._meta.verbose_name, ident)}
        context.update(extra_context or {})
        return super(ManageBillLineAdmin, self).add_view(request, form_url, extra_context=context)

    def change_view(self, request, bill_line_id, object_id, extra_context=None):
        return super(ManageBillLineAdmin, self).change_view(request, bill_line_id, extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            bill = self.get_bill(request)
            if self.model is BudgetLine:
                obj.budget_id = bill.pk
            else:
                obj.order_id = 0
                obj.bill_id = bill.pk
        super(ManageBillLineAdmin, self).save_model(request, obj, form, change)


BILL_STATE_COLORS = {settings.OPEN: "grey",
                     settings.CLOSED: "blue",
                     settings.SEND: "darkorange",
                     settings.RETURNED: "magenta",
                     settings.PAYD: "green",
                     settings.IRRECOVRABLE: "red",}


def colored_status(bill):
    state = escape(bill.status)
    color = BILL_STATE_COLORS.get(bill.status, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)
colored_status.short_description = _("Status")
colored_status.allow_tags = True
colored_status.admin_order_field = 'status'


def total_bold(bill):
    return "<b>%s</b>" % bill.total
total_bold.short_description = _('Total')
total_bold.allow_tags = True


def num_lines(bill):
    return bill.lines.all().count()
num_lines.short_description = _("#Lines")


def change_link(bill):
    return get_bill_change_link(bill)
change_link.short_description = _("Bill")
change_link.allow_tags = True
change_link.admin_order_field = 'ident'


def contact_link(bill):
    url = reverse('admin:contacts_contact_change', args=[bill.contact.pk])
    return '<a href="%s">%s</a>' % (url, bill.contact)
contact_link.short_description = _("Contact")
contact_link.allow_tags = True
contact_link.admin_order_field = 'contact'


# we inherit from ContactSupportAdminMixin in order to have the intermediary page.
class BillAdmin(admin.ModelAdmin):
    list_display = (change_link, colored_status, total_bold, num_lines, contact_link, 'comments', 'date', 'modified', )
    date_hierarchy = ('date')
    search_fields = ('contact__name', 'contact__surname', 'ident',)
    list_filter = ('status',)
    actions = [close_selected, send_selected, amend_selected, merge_selected,
               mark_as_returned, mark_as_payd, mark_as_irrecovrable, bulk_download]
    change_form_template = "admin/billing/bill/change_form.html"
    inlines = []
    
    def __init__(self, model, adminsite):
        self.fieldsets = ((None,   {'fields': (('ident'),
                                               ('status',),
                                               ('date',),
                                               ('due_date',),
                                               ('comments'),)}),
                          ('HTML', {'classes': ('collapse',),
                                    'fields': (('html'),)}),)
        self.form = get_bill_form(model)  
        self.bill_super_class = Bill
        #TODO: this is pure crap, refactor, split this or make it minimum understandable.
        #TODO: why this __init__ method is called so many times?
        #TODO: refactor this class spliting in a BaseBillAdmin or something
        if model is Budget:
            self.bill_super_class = Budget
            self.inlines = [BudgetLineTabularInline,]     
        elif model in (AmendmentInvoice, AmendmentFee):
            self.inlines = [AmendedBillLineTabularInline,]
            self.change_list_template = "admin/billing/bill/change_list.html"
        else:
            if not BillLineTabularInline in self.inlines:
                self.inlines.append(BillLineTabularInline)
            self.change_list_template = "admin/billing/bill/change_list.html"
        super(BillAdmin, self).__init__(model, adminsite)

    def get_actions(self, request):
        actions = super(BillAdmin, self).get_actions(request)
        if self.model is Budget and 'amend_selected' in actions:
            del actions['amend_selected']
            del actions['mark_as_returned']
            del actions['mark_as_payd']
            del actions['mark_as_irrecovrable']
        return actions 

    def get_urls(self):
        """Returns the additional urls used by the Contact admin."""
        from django.conf.urls.defaults import include
        urls = super(BillAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.module_name
        if self.model is Budget: line_cls = BudgetLine
        if self.model is Invoice: line_cls = InvoiceLine
        if self.model is Fee: line_cls = FeeLine
        if self.model is AmendmentInvoice: line_cls = AmendedInvoiceLine
        if self.model is AmendmentFee: line_cls = AmendedFeeLine
        if self.model is Bill: line_cls = BillLine
        #TODO: prevent to access this urls if object is not in the proper state
        select_urls = patterns("",
            url("/select_contact/$", admin_site.admin_view(select_contact_view), {'model_admin': self}, name='%s_%s_select_contact' % info),
            url("^(?P<object_id>\d+)/action/(?P<action>[a-z]+)/$", admin_site.admin_view(self.action_view), name='%s_%s_action' % info),
            url("^(?P<bill_id>\d+)/manage_lines/$", admin_site.admin_view(self.manage_bill_lines), name='%s_%s_manage_lines' % info),
            url("^(?P<object_id>\d+)/manage_lines/", include(ManageBillLineAdmin(line_cls, admin_site).get_urls())),       
#            url("^(?P<bill_id>\d+)/select_to_move/", include(BillListAdmin(self.model, admin_site).get_urls())),       
            url("^(.*)/select_to_move/", include(BillListAdmin(self.model, admin_site).get_urls())),  
            url("^(.+)/get_pdf/$", admin_site.admin_view(self.get_pdf_view), name='%s_%s_get_pdf' % info),)
        return select_urls + urls     

    def changelist_view(self, request, extra_context=None):
        if self.model is not Budget:
            path = request.META['PATH_INFO']
            replace = "/%s/" % (path.split('/billing/')[1].split('/')[0])
            query_string = request.META['QUERY_STRING']
            add_links = []
            if self.model == Bill:
                path_add = path + 'add/'
                current = mark_safe(u'<li class="selected"><a href="./?%s">All</a></li>' % (query_string))
                for subclass in Bill.get_subclasses():
                    url = path_add.replace(replace, "/%s/" % subclass.__name__.lower() )
                    lower = subclass.__name__.lower() 
                    verbose = subclass._meta.verbose_name.capitalize()
                    head = mark_safe(u'<li><a href="%s' % url)
                    tail = mark_safe(u'  %s </a></li>' % (verbose))
                    add_links.append([head, tail])
            else:
                url = path.replace(replace, "/bill/" )
                current = mark_safe(u'<li><a href="%s?%s">All</a></li>' % (url, query_string))
            
            bill_type_filter = [current]
            for subclass in Bill.get_subclasses():
                url = path.replace(replace, "/%s/" % subclass.__name__.lower() )
                verbose = subclass._meta.verbose_name.capitalize()
                if subclass == self.model:
                    current = mark_safe(u'<li class="selected"><a href="./?%s">%ss</a></li>' % (query_string, verbose))
                    if not add_links:

                        head = mark_safe(u'<li><a href="%sadd/' % (url))
                        tail = mark_safe(u'  %s </a></li>' % (verbose))
                        add_links = [[head, tail]]
                else:
                    current = mark_safe(u'<li><a href="%s?%s">%s</a></li>' % (url, query_string, verbose))
                bill_type_filter.append(current)
                
            context = { "bill_type_filter": bill_type_filter,
                        "add_links": add_links }
        else: context = {}
        context.update(extra_context or {})
        return super(BillAdmin, self).changelist_view(request, extra_context=context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        from django.contrib.contenttypes.models import ContentType
        from django.template.response import TemplateResponse
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        status = obj.status if obj else None

        context.update({
            'add': add,
            'change': change,
            'status': status,
            'settings': settings,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
        })
        if add and self.add_form_template is not None:
            form_template = self.add_form_template
        else:
            form_template = self.change_form_template

        return TemplateResponse(request, form_template or [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ], context, current_app=self.admin_site.name)    
    
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if not obj.pk:
            obj.contact_id = request.GET['contact_id']
            obj.ident = self.model.get_new_open_ident()
        obj.save()
        
    def change_view(self, request, object_id, extra_context=None):
        """ Show contact name on form title. """
        obj = self.get_object(request, object_id)
        opts = self.model._meta
        context = { 
            'title': _('Change %s of contact %s') % (opts.verbose_name, obj.contact.fullname),
            'bill_type': self.bill_super_class.__name__.lower() }
        context.update(extra_context or {})
#        return super(ContactSupportAdminMixin, self).change_view(request, object_id, extra_context=context)    
        return super(BillAdmin, self).change_view(request, object_id, extra_context=context)    

    def add_view(self, request, form_url='', extra_context=None):
    
        """ Override add view title """
        context = {'bill_type': self.bill_super_class.__name__.lower()}
        if 'contact_id' in request.GET:
            contact_id = request.GET['contact_id']
            contact = Contact.objects.get(pk=request.GET['contact_id'])
            opts = self.model._meta
            context.update({ 'contact_id': request.GET['contact_id'],
                             'content_title': _('Add %s for contact %s') % (opts.verbose_name, contact.fullname)})
            context.update(extra_context or {})        
            return super(BillAdmin, self).add_view(request, form_url='', extra_context=context)
        else: return HttpResponseRedirect("./select_contact/")    
    
    @transaction.commit_on_success         
    def action_view(self, request, object_id, action, extra_context=None): 
        bill = self.model.objects.get(pk=object_id)
        if action == 'close':
            bill.close()
            msg = 'succesfully closed'
        elif action == 'send':
            bill.send()
            msg = 'succesfully sent'                
        elif action == 'returned':
            bill.mark_as_returned()
            msg = 'marked as returned'                
        elif action == 'payd': 
            bill.mark_as_payd()
            msg = 'marked as payd'                
        elif action == 'irrecovrable':
            bill.mark_as_irrecovrable()
            msg = 'marked as irrecovrable debt'                
        bill_type = self.model.__name__.lower()
        self.message_user(request, _("%s %s" % (bill_type.capitalize(), msg)))
        if 'HTTP_REFERER' in request.META:
            url = request.META['HTTP_REFERER']
        else: 
            url = "/admin/billing/%s/%s" % (bill_type, object_id)
        return HttpResponseRedirect(url)

    def get_pdf_view(self, request, object_id, extra_context=None):
        bill = self.model.objects.get(id=object_id)
        pdf = bill.get_pdf()
        return download_files([{'filename': "%s.pdf" % bill.ident, 
                                'file': pdf },], 
                                mimetype='application/x-pdf')
    
    def manage_bill_lines(self, request, bill_id, extra_context=None):
        bill = self.model.objects.get(id=bill_id)
        if bill.status != settings.OPEN: start = 'Amend'
        else: start = 'Manage'
        context = {'title': _('%s %s lines of %s') % (start, self.model._meta.verbose_name, bill), 
                   'bill': bill }

        #queryset = BillLine.objects.filter(bill=bill)
        line_cls = BudgetLine if self.model is Budget else BillLine
        return ManageBillLineAdmin(line_cls, self.admin_site).changelist_view(request, context)


class BillListAdmin(BillAdmin):
    """ Used for move lines """
    list_display = ['ident', 'contact',]
    actions = None
    search_fields = ['ident', 'contact__name',]
    list_filter = ()
    change_form_template = "admin/billing/bill/change_form.html"
    fieldsets = ((None,     {'fields': (('ident'),
                                        ('status',),
                                        ('date'),
                                        ('due_date'),
                                        ('comments'),)}),
                ('HTML', {'classes': ('collapse',),
                          'fields': (('html'),)}),)

    def get_urls(self):
        return super(BillAdmin, self).get_urls()
    
    def changelist_view(self, request, extra_context=None):
        """Renders the change view."""
        self.change_list_template = 'admin/billing/billline/select_bill.html'
        bill_id = request.META['PATH_INFO'].split('/select_to_move/')[0].split('/')[-1]
        req = request.GET.copy()
        if 'queryset' in req:
            queryset = req.pop('queryset')[0]
        else:
            if 'HTTP_REFERER' in request.META:
                queryset = request.META['HTTP_REFERER'].split('queryset=')[1]
                end = "select_to_move/?%s&queryset=%s" % (request.GET.urlencode(), queryset)
            else: end = ''
            url = "/admin/billing/%s/%s/%s" % (self.model.__name__.lower(), bill_id, end)
            return HttpResponseRedirect(url)   
             
        def add_to_bill_link(self):
            url = "../manage_lines/move/?bill_lines=%s&bill_id=%s" % (queryset, self.id)
            return '<a href="%(url)s">%(bill_ident)s</a>' % {'url': url , 'bill_ident': self.ident  }

        add_to_bill_link.short_description = _("Bill")
        add_to_bill_link.allow_tags = True
        
        self.list_display = (add_to_bill_link, 'contact', 'date')
        self.list_display_links = (add_to_bill_link,)
        self.date_hierarchy = ('date')
        
        # Only show invoices with status = Open
        req['status'] = settings.OPEN
        request.GET = req
        request.META['QUERY_STRING'] = request.GET.urlencode()
        opts = self.model._meta
        bill = self.model.objects.get(id=bill_id)
        context = { 'title': _('Select the bill where do you want to move selected lines'),
                    'bill': bill,
                    'bill_type': self.model.__name__.lower() }
        context.update(extra_context or {})
        return super(BillListAdmin, self).changelist_view(request, context)    

    def add_view(self, request, form_url='', extra_context=None):
        return super(BillListAdmin, self).add_view(request, form_url, extra_context)


admin.site.register(BillLine)
admin.site.register(Bill, BillAdmin)
admin.site.register(Invoice, BillAdmin)
admin.site.register(Fee, BillAdmin)
admin.site.register(AmendmentInvoice, BillAdmin)
admin.site.register(AmendmentFee, BillAdmin)
admin.site.register(Budget, BillAdmin)

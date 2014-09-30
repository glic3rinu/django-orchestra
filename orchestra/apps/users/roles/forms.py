from django import forms


class RoleAdminBaseForm(forms.ModelForm):
    class Meta:
        exclude = ('user', )
    
    def save(self, *args, **kwargs):
        self.instance.user = self.user
        return super(RoleAdminBaseForm, self).save(*args, **kwargs)


def role_form_factory(role):
    class RoleAdminForm(RoleAdminBaseForm):
        class Meta(RoleAdminBaseForm.Meta):
            model = role.model
    return RoleAdminForm

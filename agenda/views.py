from django.db.models import Q
from django.shortcuts import redirect, render
from .forms import ContactoForm
from .models import contacto

def mostrar_agenda(request):
    q = request.GET.get('q', '')
    contactos = contacto.objects.filter(Q(nombre__icontains=q) | Q(correo__icontains=q))
    form = ContactoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('mostrar_agenda')
    return render(request, 'contactos/contactos.html', {'contactos': contactos, 'form': form, 'q': q})



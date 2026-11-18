from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def cadastro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, "Conta criada. Você já está dentro.")
            return redirect("catalogo:home")
    else:
        form = UserCreationForm()
    return render(request, "contas/cadastro.html", {"form": form})

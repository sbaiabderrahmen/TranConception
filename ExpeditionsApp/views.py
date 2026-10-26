from django.http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("welcome to the Expeditions App!")

def afficher(request,name):
    return render(request, 'expedition/afficher.html', {'name': name})

def list_expeditions(request):
    expeditions = Expedition.objects.all()
    return render(request, 'expedition/list_expeditions.html', {'expeditions': expeditions})

def detailExpedition(request, reference):
    expedition = Expedition.objects.get(reference=reference)
    return render(request, 'expedition/detail_expedition.html', {'expedition': expedition})
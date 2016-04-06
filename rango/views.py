from django.http import HttpResponse

def index(request):
	return HttpResponse("Rango says hey there world<br><a href='/rango/about/'>about</a>")
def about(request):
	return HttpResponse("About page<br><a href='/rango/'>back</a>")
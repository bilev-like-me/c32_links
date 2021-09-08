from django.shortcuts import render
from django.views import View

class MainView(View):
    def get(self, request):
        return render(request, "index.html")
    
    def post(self, request):
        print(request.POST['link'])
        return render(request, "index.html")

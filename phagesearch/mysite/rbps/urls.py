from django.urls import path, re_path
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path('host-suggestions/', views.host_suggestions, name='host-suggestions'),
    path('sequence/<int:sequence_pk>/', views.sequence_detail, name='sequence_detail'),
    # An additional pattern for downloading the PDB file
    path('sequence/<int:sequence_pk>/download/', lambda request, sequence_pk: views.sequence_detail(request, sequence_pk, download_pdb=True), name='download_pdb'),
    path('download-sequences/', views.download_sequences, name='download_sequences'),
    path('host-suggestions/', views.host_suggestions, name='host-suggestions'),
    path('analysis/', views.analysis, name='analysis'),
    path('protein-analysis/', views.protein_analysis, name='protein_analysis'),
    path('download_structures/', views.download_structures, name='download_structures'),
    path('sequence/<int:sequence_pk>/esmfold_prediction/', views.esmfold_prediction, name='esmfold_prediction'),
    path('sequence/<int:sequence_pk>/esmfold_prediction/download/', lambda request, sequence_pk: views.esmfold_prediction(request, sequence_pk, download_pdb_esm=True), name='download_pdb_esm'),
    path('about/', views.about, name='about'),
    path('overview/', views.overview, name='overview'),
]


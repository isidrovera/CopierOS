# -*- coding: utf-8 -*-
from django.urls import path

from .views import (
    ArchivePartnerBranchView,
    ArchivePartnerContactView,
    ArchivePartnerView,
    DocumentLookupLogListView,
    PartnerBranchDetailUpdateView,
    PartnerBranchListCreateView,
    PartnerContactDetailUpdateView,
    PartnerContactListCreateView,
    PartnerDetailUpdateView,
    PartnerListCreateView,
    RestorePartnerBranchView,
    RestorePartnerContactView,
    RestorePartnerView,
)


app_name = "partners"


urlpatterns = [
    path(
        "",
        PartnerListCreateView.as_view(),
        name="partner-list-create",
    ),

    path(
        "branches/",
        PartnerBranchListCreateView.as_view(),
        name="branch-list-create",
    ),
    path(
        "branches/<uuid:id>/",
        PartnerBranchDetailUpdateView.as_view(),
        name="branch-detail-update",
    ),
    path(
        "branches/<uuid:branch_id>/archive/",
        ArchivePartnerBranchView.as_view(),
        name="branch-archive",
    ),
    path(
        "branches/<uuid:branch_id>/restore/",
        RestorePartnerBranchView.as_view(),
        name="branch-restore",
    ),

    path(
        "contacts/",
        PartnerContactListCreateView.as_view(),
        name="contact-list-create",
    ),
    path(
        "contacts/<uuid:id>/",
        PartnerContactDetailUpdateView.as_view(),
        name="contact-detail-update",
    ),
    path(
        "contacts/<uuid:contact_id>/archive/",
        ArchivePartnerContactView.as_view(),
        name="contact-archive",
    ),
    path(
        "contacts/<uuid:contact_id>/restore/",
        RestorePartnerContactView.as_view(),
        name="contact-restore",
    ),

    path(
        "document-lookups/",
        DocumentLookupLogListView.as_view(),
        name="document-lookup-list",
    ),

    path(
        "<uuid:partner_id>/archive/",
        ArchivePartnerView.as_view(),
        name="partner-archive",
    ),
    path(
        "<uuid:partner_id>/restore/",
        RestorePartnerView.as_view(),
        name="partner-restore",
    ),
    path(
        "<uuid:id>/",
        PartnerDetailUpdateView.as_view(),
        name="partner-detail-update",
    ),
]
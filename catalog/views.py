"""Catalog screens (plan §4.1, G07). Views only call forms and services."""

from __future__ import annotations

from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from accounts.permissions import staff_view
from administration.errors import RuleViolation

from . import services
from .forms import AddCopiesForm, BookForm, LabelSelectionForm
from .models import Book, CopyStatus


def _get_book(pk: int) -> Book:
    book = services.get_book(pk)
    if book is None:
        raise Http404("Kitap bulunamadı")
    return book


@staff_view
@require_http_methods(["GET"])
def book_search(request: HttpRequest) -> HttpResponse:
    q = request.GET.get("q", "").strip()
    results = services.search_books(q) if q else []
    matched_copy = None
    if results and services.is_barcode(q):
        try:
            matched_copy = services.find_copy(q)
        except RuleViolation:
            matched_copy = None
    counts = services.shelf_counts(results)
    rows = [(book, *counts[book.pk]) for book in results]
    context = {"q": q, "rows": rows, "matched_copy": matched_copy}
    return render(request, "catalog/search.html", context)


def _save_book(request: HttpRequest, form: BookForm, book: Book | None) -> Book | None:
    """Create or update from a valid form; a RuleViolation becomes a form error."""
    data = form.cleaned_data
    values = {
        "title": data["title"],
        "author": data["author"],
        "isbn13": data["isbn"],
        "publisher": data["publisher"],
        "year": data["year"],
    }
    try:
        if book is None:
            return services.create_book(request.user, **values)
        return services.update_book(request.user, book, **values)
    except RuleViolation as exc:
        form.add_error(None, exc.message)
        return None


@staff_view
@require_http_methods(["GET", "POST"])
def book_create(request: HttpRequest) -> HttpResponse:
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        book = _save_book(request, form, None)
        if book is not None:
            messages.success(request, "Kitap kaydedildi")
            return redirect("catalog:detail", pk=book.pk)
    return render(request, "catalog/form.html", {"form": form, "book": None})


@staff_view
@require_http_methods(["GET", "POST"])
def book_edit(request: HttpRequest, pk: int) -> HttpResponse:
    book = _get_book(pk)
    if request.method == "GET":
        form = BookForm(
            initial={
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn13 or "",
                "publisher": book.publisher or "",
                "year": book.year,
            }
        )
    else:
        form = BookForm(request.POST)
        if form.is_valid() and _save_book(request, form, book) is not None:
            messages.success(request, "Kitap bilgileri kaydedildi")
            return redirect("catalog:detail", pk=pk)
    return render(request, "catalog/form.html", {"form": form, "book": book})


def _detail_page(request: HttpRequest, book: Book, *, copies_form=None) -> HttpResponse:
    copies = services.book_copies(book)
    context = {
        "book": book,
        "copies": copies,
        "has_printable": any(copy.status != CopyStatus.WITHDRAWN for copy in copies),
        "copies_form": copies_form or AddCopiesForm(),
    }
    return render(request, "catalog/detail.html", context)


@staff_view
@require_http_methods(["GET"])
def book_detail(request: HttpRequest, pk: int) -> HttpResponse:
    return _detail_page(request, _get_book(pk))


@staff_view
@require_POST
def book_add_copies(request: HttpRequest, pk: int) -> HttpResponse:
    book = _get_book(pk)
    form = AddCopiesForm(request.POST)
    if form.is_valid():
        try:
            copies = services.add_copies(request.user, book, form.cleaned_data["count"])
        except RuleViolation as exc:
            form.add_error("count", exc.message)
        else:
            messages.success(request, f"{len(copies)} nüsha eklendi")
            return redirect("catalog:detail", pk=pk)
    return _detail_page(request, book, copies_form=form)


@staff_view
@require_http_methods(["GET", "POST"])
def label_print(request: HttpRequest) -> HttpResponse:
    """GET: the range form; POST: a range or ``copy_ids`` -> label PDF (ADR-0036)."""
    form = LabelSelectionForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            copy_ids = services.copies_for_labels(data["copy_ids"], data["start"], data["end"])
        except RuleViolation as exc:
            form.add_error(None, exc.message)
        else:
            response = HttpResponse(services.label_pdf(copy_ids), content_type="application/pdf")
            response["Content-Disposition"] = 'inline; filename="etiketler.pdf"'
            return response
    return render(request, "catalog/label_range.html", {"form": form})

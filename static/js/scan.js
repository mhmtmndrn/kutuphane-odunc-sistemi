/* Focus handling for barcode scanning (FR-11, NFR-11, plan G11).
 *
 * A USB scanner types the code and presses Enter. The forms work without
 * this script; it only moves the focus:
 * - On load (and when the page comes back from the browser cache) the
 *   element with the autofocus attribute gets the focus and its text is
 *   selected, so the next scan replaces it.
 * - Enter in a field with data-next-focus="<id>" moves the focus to that
 *   element when it is an empty field of the same form, instead of
 *   submitting the form.
 */
(function () {
  "use strict";

  function focusAutofocus() {
    var element = document.querySelector("[autofocus]");
    if (!element) {
      return;
    }
    element.focus();
    if (typeof element.select === "function") {
      element.select();
    }
  }

  function onKeydown(event) {
    if (event.key !== "Enter") {
      return;
    }
    var field = event.target;
    var targetId = field.getAttribute && field.getAttribute("data-next-focus");
    if (!targetId) {
      return;
    }
    var target = document.getElementById(targetId);
    if (target && target.form === field.form && target.value === "") {
      event.preventDefault();
      target.focus();
    }
  }

  document.addEventListener("DOMContentLoaded", focusAutofocus);
  window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
      focusAutofocus();
    }
  });
  document.addEventListener("keydown", onKeydown);
})();

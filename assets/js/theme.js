(function () {
  "use strict";

  var storageKey = "theme";
  var root = document.documentElement;
  var button;
  var label;

  function applyTheme(theme) {
    var isDark = theme === "dark";
    root.setAttribute("data-theme", isDark ? "dark" : "light");
    document.querySelector('meta[name="theme-color"]').setAttribute(
      "content", isDark ? "#111113" : "#fcfcfa"
    );

    if (button) {
      label.textContent = isDark ? "Light mode" : "Dark mode";
      button.setAttribute("aria-label", "Switch to " + label.textContent.toLowerCase());
    }
  }

  // Restore before styles load to avoid flashing the wrong theme.
  var savedTheme;
  try {
    savedTheme = window.localStorage.getItem(storageKey);
  } catch (error) {
    // The toggle still works when browser storage is unavailable.
  }
  applyTheme(savedTheme);

  document.addEventListener("DOMContentLoaded", function () {
    button = document.getElementById("theme-toggle");
    label = document.getElementById("theme-toggle-label");
    if (!button || !label) return;

    applyTheme(root.getAttribute("data-theme"));
    button.hidden = false;
    button.addEventListener("click", function () {
      var theme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(theme);
      try {
        window.localStorage.setItem(storageKey, theme);
      } catch (error) {
        // Keep the current page usable even if saving the preference fails.
      }
    });
  });

  window.addEventListener("storage", function (event) {
    if (event.key === storageKey || event.key === null) {
      applyTheme(event.newValue);
    }
  });
})();

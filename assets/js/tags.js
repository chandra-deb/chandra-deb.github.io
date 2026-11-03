(function () {
  "use strict";

  var params = new URLSearchParams(window.location.search);
  var activeTag = params.get("tag");
  if (!activeTag) return;

  var posts = Array.prototype.slice.call(
    document.querySelectorAll("[data-post-tags]")
  );
  var chips = Array.prototype.slice.call(
    document.querySelectorAll("[data-filter-tag]")
  );
  var status = document.getElementById("tag-status");
  var activeChip = null;
  var count = 0;

  chips.forEach(function (chip) {
    var isActive = chip.getAttribute("data-filter-tag") === activeTag;
    chip.classList.toggle("is-active", isActive);
    chip.setAttribute("aria-current", isActive ? "true" : "false");
    if (isActive) activeChip = chip;
  });

  posts.forEach(function (post) {
    var tags = (post.getAttribute("data-post-tags") || "")
      .split("|")
      .filter(Boolean);
    var matches = tags.indexOf(activeTag) !== -1;
    post.hidden = !matches;
    if (matches) count += 1;
  });

  if (status) {
    var name = activeChip
      ? activeChip.getAttribute("data-filter-name")
      : activeTag;

    if (count === 0) {
      status.textContent = 'No posts tagged "' + name + '".';
    } else {
      status.textContent =
        count + " post" + (count === 1 ? "" : "s") + ' tagged "' + name + '".';
    }
  }
})();

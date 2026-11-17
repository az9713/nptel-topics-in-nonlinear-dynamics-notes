"use strict";

const hiddenSolutions = new Set();

window.addEventListener("beforeprint", () => {
  for (const details of document.querySelectorAll("details")) {
    if (!details.open) {
      hiddenSolutions.add(details);
      details.open = true;
    }
  }
});

window.addEventListener("afterprint", () => {
  for (const details of hiddenSolutions) details.open = false;
  hiddenSolutions.clear();
});

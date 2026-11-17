"use strict";

const controls = document.querySelector(".search");
const input = document.querySelector("#chapter-query");
const count = document.querySelector("#chapter-count");
const lists = [...document.querySelectorAll(".chapters")];
const cards = lists.flatMap(list => [...list.children]);

function filterChapters() {
  const words = input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const card of cards) {
    const chapterText = card.textContent.toLowerCase();
    card.hidden = !words.every(word => chapterText.includes(word));
    if (!card.hidden) visible += 1;
  }
  for (const list of lists) {
    if (list.parentElement.matches("section")) {
      list.parentElement.hidden = [...list.children].every(card => card.hidden);
    }
  }
  count.textContent = words.length ? `${visible} matching chapters` : "";
}

controls.hidden = false;
input.addEventListener("input", filterChapters);

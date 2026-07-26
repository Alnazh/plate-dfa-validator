// Force the plate input to uppercase as the user types
const plateInput = document.getElementById("plate");

if (plateInput) {
  plateInput.addEventListener("input", () => {
    const cursor = plateInput.selectionStart;
    plateInput.value = plateInput.value.toUpperCase();
    plateInput.setSelectionRange(cursor, cursor);
  });
}

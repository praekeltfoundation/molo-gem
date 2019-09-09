export default (text = "Hello component world") => {
  const element = document.createElement("div");

  element.innerHTML = text;
  return element;
};

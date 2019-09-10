import React from "react"
import ReactDOM from "react-dom"
import component from "./component";

const mainReactDiv = document.getElementById("react");
mainReactDiv.classList.add('react-wrapper');


function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
const element = <Welcome name="world" />;

ReactDOM.render(
  element,
  mainReactDiv
);

mainReactDiv.appendChild(component());

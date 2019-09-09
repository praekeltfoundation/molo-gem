import React from "react"
import ReactDOM from "react-dom"
import component from "./component";

document.body.appendChild(component());

function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
const element = <Welcome name="world" />;
ReactDOM.render(
  element,
  document.getElementById("react")
);

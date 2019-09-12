import React from "react"
import ReactDOM from "react-dom"

function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
const element = <Welcome name="world" />;

const mainReactDiv = document.getElementById("react");
ReactDOM.render(
  element,
  mainReactDiv
)

import React from "react"
import ReactDOM from "react-dom"
//import {MoloComp} from "../Components/molo.jsx"

function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
const element = <Welcome name="world" />;

ReactDOM.render(
  element,
  //<MoloComp />,
  document.querySelector("#react")
)

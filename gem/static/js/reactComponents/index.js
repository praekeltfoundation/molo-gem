import { hot } from 'react-hot-loader/root';
import React from "react"
import ReactDOM from "react-dom"
import component from "./Components/component";

const mainReactDiv = document.getElementById("react");
mainReactDiv.classList.add('react-wrapper');

function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
const element = <Welcome name="world" />;

mainReactDiv.appendChild(component())
const App = () => {
  ReactDOM.render(
    element,
    mainReactDiv
  )
}

export default hot(App);

import React from "react"
import ReactDOM from "react-dom"


class Language extends React.Component {
  render() {
    var list = window.props;
    return <ul className="questionare">{list.map(item => <LanguageChild key={item.pk} question={item.questionnaire_text}/> )}</ul>;
  }
}

class LanguageChild extends React.Component {
  render() {
    return <li className="questionare__item">{this.props.question}</li>;
  }
}

ReactDOM.render(
  <Language />,
  window.react_mount
)

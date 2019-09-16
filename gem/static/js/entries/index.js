import React from "react"
import ReactDOM from "react-dom"


class Language extends React.Component {
    render() {
        var list = window.props;
        return <div>{list.map(item => <TestChild key={item.pk}
                        question={item.question_text}/> )}</div>;
    }
}

class LanguageChild extends React.Component {
    render() {
     return <li><b>{this.props.question}</b></li>;
    }
}

ReactDOM.render(
  <Language />,
  document.getElementById('react')
)

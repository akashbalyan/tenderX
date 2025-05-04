import TenderList from "./components/TenderList"
import "./components/TenderList.css"

function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>Tenders</h1>
      </header>
      <main className="main-content">
        <TenderList />
      </main>
    </div>
  )
}

export default App
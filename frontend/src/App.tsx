import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Dashboard } from "./components/Dashboard";
import { History } from "./components/History";
import { Layout } from "./components/Layout";
import { Settings } from "./components/Settings";
import { Skills } from "./components/Skills";
import { Workflows } from "./components/Workflows";
import { LanguageProvider } from "./i18n/LanguageContext";

function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="skills" element={<Skills />} />
            <Route path="workflows" element={<Workflows />} />
            <Route path="history" element={<History />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;

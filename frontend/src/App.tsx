import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Dashboard } from "./components/Dashboard";
import { History } from "./components/History";
import { Layout } from "./components/Layout";
import { Settings } from "./components/Settings";
import { Skills } from "./components/Skills";
import { Workflows } from "./components/Workflows";
import { LanguageProvider } from "./i18n/LanguageContext";
import { Projects } from "./components/Projects";
import { Ideas } from "./components/Ideas";
import { Personas } from "./components/Personas";
import { Offers } from "./components/Offers";
import { LandingPages } from "./components/LandingPages";
import { Outreach } from "./components/Outreach";
import { Leads } from "./components/Leads";
import { Deals } from "./components/Deals";
import { Proposals } from "./components/Proposals";
import { Delivery } from "./components/Delivery";
import { Revenue } from "./components/Revenue";
import { BusinessDashboard } from "./components/BusinessDashboard";

function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="overview" element={<BusinessDashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="ideas" element={<Ideas />} />
            <Route path="personas" element={<Personas />} />
            <Route path="offers" element={<Offers />} />
            <Route path="landing-pages" element={<LandingPages />} />
            <Route path="outreach" element={<Outreach />} />
            <Route path="leads" element={<Leads />} />
            <Route path="deals" element={<Deals />} />
            <Route path="proposals" element={<Proposals />} />
            <Route path="delivery" element={<Delivery />} />
            <Route path="revenue" element={<Revenue />} />
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

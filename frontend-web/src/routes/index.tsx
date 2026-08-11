import { createBrowserRouter } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

import Home from "../pages/Home/Home";
import Detection from "../pages/Detection/Detection";
import History from "../pages/History/History";
import Education from "../pages/Education/Education";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Home />
      },
      {
        path: "detection",
        element: <Detection />
      },
      {
        path: "history",
        element: <History />
      },
      {
        path: "education",
        element: <Education />
      }
    ]
  }
]);

export default router;

import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'a4d'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '047'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'fa1'),
            routes: [
              {
                path: '/docs/category/unit-10---conductors-and-capacitors',
                component: ComponentCreator('/docs/category/unit-10---conductors-and-capacitors', '79b'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/category/unit-11---electric-circuits',
                component: ComponentCreator('/docs/category/unit-11---electric-circuits', 'f9e'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/category/unit-12---magnetic-fields-and-electromagnetism',
                component: ComponentCreator('/docs/category/unit-12---magnetic-fields-and-electromagnetism', '147'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/category/unit-13---electromagnetic-induction',
                component: ComponentCreator('/docs/category/unit-13---electromagnetic-induction', 'b03'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/category/unit-8---electric-charges-fields-and-gausss-law',
                component: ComponentCreator('/docs/category/unit-8---electric-charges-fields-and-gausss-law', 'f29'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/category/unit-9---electric-potential',
                component: ComponentCreator('/docs/category/unit-9---electric-potential', '3ea'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '7c1'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/Unit-10/Overview',
                component: ComponentCreator('/docs/Unit-10/Overview', '1c9'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/Unit-11/Overview',
                component: ComponentCreator('/docs/Unit-11/Overview', '125'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/Unit-12/Overview',
                component: ComponentCreator('/docs/Unit-12/Overview', '143'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/Unit-13/Overview',
                component: ComponentCreator('/docs/Unit-13/Overview', 'f25'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/Unit-8/8.1-coulomb',
                component: ComponentCreator('/docs/Unit-8/8.1-coulomb', '29b'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/Unit-8/Overview',
                component: ComponentCreator('/docs/Unit-8/Overview', '1c6'),
                exact: true,
                sidebar: "materialSidebar"
              },
              {
                path: '/docs/Unit-9/Overview',
                component: ComponentCreator('/docs/Unit-9/Overview', 'fe7'),
                exact: true,
                sidebar: "materialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];

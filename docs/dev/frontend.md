# Frontend
As with the API, MegaQC is currently transitioning from using an HTML + CSS + JavaScript 
frontend to [React](https://reactjs.org/). This can be confusing, as a number of 
technologies are mixed in the same project.

As explained above, each URL in MegaQC renders a Jinja2 template. The old-style
endpoints have a lot of HTML code in their templates that defines the entire page layout,
and load JavaScript and CSS located in the `megaqc/static` directory.

However, the newer React pages instead render a special template, called `react.html`,
which is a very simple page that acts as the entry point for the React code, which handles
all layout and logic.

The source code for this JavaScript can be found in the `src` directory, which currently
has one root-level `.js` file for each React page that then imports other components
to use.

Note that all new pages going forward should be written using React, to improve the
maintainability of the frontend.

"""
Bootstrap-based sphinx theme from the PyData community
"""
import os

from sphinx.errors import ExtensionError
from bs4 import BeautifulSoup as bs

from .bootstrap_html_translator import BootstrapHTML5Translator

__version__ = "0.4.2dev0"


from sphinx.environment.adapters.toctree import TocTree
from sphinx import addnodes
from docutils import nodes


def add_toctree_functions(app, pagename, templatename, context, doctree):
    """Add functions so Jinja templates can add toctree objects."""

    def generate_nav_html(kind, **kwargs):
        """
        Return the navigation link structure in HTML. Arguments are passed
        to Sphinx "toctree" function (context["toctree"] below).

        We use beautifulsoup to add the right CSS classes / structure for bootstrap.

        See https://www.sphinx-doc.org/en/master/templating.html#toctree.

        Parameters
        ----------
        kind : ["navbar", "sidebar", "raw"]
            The kind of UI element this toctree is generated for.
        kwargs: passed to the Sphinx `toctree` template function.

        Returns
        -------
        HTML string (if kind in ["navbar", "sidebar"])
        or BeautifulSoup object (if kind == "raw")
        """
        if kind == "navbar":
            toc_sphinx = context["toctree"](**kwargs)
            soup = bs(toc_sphinx, "html.parser")

            # pair "current" with "active" since that's what we use w/ bootstrap
            for li in soup("li", {"class": "current"}):
                li["class"].append("active")

            # Add CSS for bootstrap
            for li in soup("li"):
                li["class"].append("nav-item")
                li.find("a")["class"].append("nav-link")
            return "\n".join([ii.prettify() for ii in soup.find_all("li")])

        toc = TocTree(app.env)
        # toctree = toc.get_toctree_for(pagename, app.builder, **kwargs)
        
        # if not pagename == "demo/index":
        #     return ""
        # breakpoint()

        # toctrees_root = app.env.tocs[app.env.config['master_doc']]
        # first_pages = []
        # for toctree_root in toctrees_root.traverse(addnodes.toctree):
        #     for _, path_first_page in toctree_root.attributes.get("entries", []):
        #         first_pages.append(path_first_page)

        # toctrees_first_page = app.env.tocs[first_page]

        toc = TocTree(app.env)

        indexname = ... # get name of the page that has the toctree, eg semo/index
        index_toctree = app.env.tocs[indexname].deepcopy()
        
        toctrees = []
        for toctreenode in index_toctree.traverse(addnodes.toctree):
            toctree = toc.resolve(pagename, app.builder, toctreenode, prune=True, **kwargs)
            if toctree:
                toctrees.append(toctree)
        if not toctrees:
            return None
        new_toctree = toctrees[0]
        for toctree in toctrees[1:]:
            new_toctree.extend(toctree.children)

        toc_sphinx = app.builder.render_partial(new_toctree)["fragment"]
        soup = bs(toc_sphinx, "html.parser")

        
        
        if pagename =="demo/subpages/subpage1":
            breakpoint()
        ancestors = toc.get_toctree_ancestors(pagename)
        # includes = app.env.toctree_includes
        
        if ancestors:
            parent_name = ancestors[-1]
            toctree2 = toc.get_local_toctree_for(parent_name, pagename, app.builder, **kwargs)
            toc_sphinx = app.builder.render_partial(toctree2)["fragment"]
            soup = bs(toc_sphinx, "html.parser")
            # pair "current" with "active" since that's what we use w/ bootstrap
            for li in soup("li", {"class": "current"}):
                li["class"].append("active")

            return soup.prettify()
            
        else:
            toc_sphinx = context["toctree"](**kwargs)
        # # Now find the toctrees for each first page and see if it has a caption
        # caption_pages = []
        # for first_page in first_pages:
        #     toctrees_first_page = app.env.tocs[first_page]
        #     for toctree_first_page in toctrees_first_page.traverse(addnodes.toctree):
        #         # If the toctree has a caption, keep track of the first page
        #         caption = toctree_first_page.attributes.get("caption")
        #         if caption:
        #             _, first_entry = toctree_first_page.attributes.get("entries", [])[0]
        #             caption_pages.append((first_entry, caption))

            

        # toc_sphinx = context["toctree"](**kwargs)
        soup = bs(toc_sphinx, "html.parser")

        # pair "current" with "active" since that's what we use w/ bootstrap
        for li in soup("li", {"class": "current"}):
            li["class"].append("active")

        if kind == "navbar":
            # Add CSS for bootstrap
            for li in soup("li"):
                li["class"].append("nav-item")
                li.find("a")["class"].append("nav-link")
            out = "\n".join([ii.prettify() for ii in soup.find_all("li")])

        elif kind == "sidebar":
            # Remove sidebar links to sub-headers on the page
            for li in soup.select("li.current ul li"):
                # Remove
                if li.find("a"):
                    href = li.find("a")["href"]
                    if "#" in href and href != "#":
                        li.decompose()

            # Join all the top-level `li`s together for display
            current_subset = soup.select("li.current.toctree-l1 ul")
            if current_subset:
                out = current_subset[0].prettify()
            else:
                out = ""

        elif kind == "raw":
            out = soup

        return out

    def generate_toc_html(kind="html"):
        """Return the within-page TOC links in HTML."""

        if "toc" not in context:
            return ""

        soup = bs(context["toc"], "html.parser")

        # Add toc-hN + visible classes
        def add_header_level_recursive(ul, level):
            if level <= (context["theme_show_toc_level"] + 1):
                ul["class"] = ul.get("class", []) + ["visible"]
            for li in ul("li", recursive=False):
                li["class"] = li.get("class", []) + [f"toc-h{level}"]
                ul = li.find("ul", recursive=False)
                if ul:
                    add_header_level_recursive(ul, level + 1)

        add_header_level_recursive(soup.find("ul"), 1)

        # Add in CSS classes for bootstrap
        for ul in soup("ul"):
            ul["class"] = ul.get("class", []) + ["nav", "section-nav", "flex-column"]

        for li in soup("li"):
            li["class"] = li.get("class", []) + ["nav-item", "toc-entry"]
            if li.find("a"):
                a = li.find("a")
                a["class"] = a.get("class", []) + ["nav-link"]

        # If we only have one h1 header, assume it's a title
        h1_headers = soup.select(".toc-h1")
        if len(h1_headers) == 1:
            title = h1_headers[0]
            # If we have no sub-headers of a title then we won't have a TOC
            if not title.select(".toc-h2"):
                out = ""
            else:
                out = title.find("ul").prettify()
        # Else treat the h1 headers as sections
        else:
            out = soup.prettify()

        # Return the toctree object
        if kind == "html":
            return out
        else:
            return soup

    def get_nav_object(maxdepth=None, collapse=True, includehidden=True, **kwargs):
        """Return a list of nav links that can be accessed from Jinja.

        Parameters
        ----------
        maxdepth: int
            How many layers of TocTree will be returned
        collapse: bool
            Whether to only include sub-pages of the currently-active page,
            instead of sub-pages of all top-level pages of the site.
        kwargs: key/val pairs
            Passed to the `toctree` Sphinx method
        """
        toc_sphinx = context["toctree"](
            maxdepth=maxdepth, collapse=collapse, includehidden=includehidden, **kwargs
        )
        soup = bs(toc_sphinx, "html.parser")

        # # If no toctree is defined (AKA a single-page site), skip this
        # if toctree is None:
        #     return []

        nav_object = soup_to_python(soup, only_pages=True)
        return nav_object

    def get_page_toc_object():
        """Return a list of within-page TOC links that can be accessed from Jinja."""

        if "toc" not in context:
            return ""

        soup = bs(context["toc"], "html.parser")

        try:
            toc_object = soup_to_python(soup, only_pages=False)
        except Exception:
            return []

        # If there's only one child, assume we have a single "title" as top header
        # so start the TOC at the first item's children (AKA, level 2 headers)
        if len(toc_object) == 1:
            return toc_object[0]["children"]
        else:
            return toc_object

    def navbar_align_class():
        """Return the class that aligns the navbar based on config."""
        align = context.get("theme_navbar_align", "content")
        align_options = {
            "content": ("col-lg-9", "mr-auto"),
            "left": ("", "mr-auto"),
            "right": ("", "ml-auto"),
        }
        if align not in align_options:
            raise ValueError(
                (
                    "Theme optione navbar_align must be one of"
                    f"{align_options.keys()}, got: {align}"
                )
            )
        return align_options[align]

    context["generate_nav_html"] = generate_nav_html
    context["generate_toc_html"] = generate_toc_html
    context["get_nav_object"] = get_nav_object
    context["get_page_toc_object"] = get_page_toc_object
    context["navbar_align_class"] = navbar_align_class


def soup_to_python(soup, only_pages=False):
    """
    Convert the toctree html structure to python objects which can be used in Jinja.

    Parameters
    ----------
    soup : BeautifulSoup object for the toctree
    only_pages : bool
        Only include items for full pages in the output dictionary. Exclude
        anchor links (TOC items with a URL that starts with #)

    Returns
    -------
    nav : list of dicts
        The toctree, converted into a dictionary with key/values that work
        within Jinja.
    """
    # toctree has this structure (caption only for toctree, not toc)
    #   <p class="caption">...</span></p>
    #   <ul>
    #       <li class="toctree-l1"><a href="..">..</a></li>
    #       <li class="toctree-l1"><a href="..">..</a></li>
    #       ...

    def extract_level_recursive(ul, navs_list):

        for li in ul.find_all("li", recursive=False):
            ref = li.a
            url = ref["href"]
            title = "".join(map(str, ref.contents))
            active = "current" in li.get("class", [])

            # If we've got an anchor link, skip it if we wish
            if only_pages and "#" in url and url != "#":
                continue

            # Converting the docutils attributes into jinja-friendly objects
            nav = {}
            nav["title"] = title
            nav["url"] = url
            nav["active"] = active

            navs_list.append(nav)

            # Recursively convert children as well
            nav["children"] = []
            ul = li.find("ul", recursive=False)
            if ul:
                extract_level_recursive(ul, nav["children"])

    navs = []
    for ul in soup.find_all("ul", recursive=False):
        extract_level_recursive(ul, navs)
    return navs


# -----------------------------------------------------------------------------


def setup_edit_url(app, pagename, templatename, context, doctree):
    """Add a function that jinja can access for returning the edit URL of a page."""

    def get_edit_url():
        """Return a URL for an "edit this page" link."""
        required_values = ["github_user", "github_repo", "github_version"]
        for val in required_values:
            if not context.get(val):
                raise ExtensionError(
                    "Missing required value for `edit this page` button. "
                    "Add %s to your `html_context` configuration" % val
                )

        # Enable optional custom github url for self-hosted github instances
        github_url = "https://github.com"
        if context.get("github_url"):
            github_url = context["github_url"]

        github_user = context["github_user"]
        github_repo = context["github_repo"]
        github_version = context["github_version"]
        file_name = f"{pagename}{context['page_source_suffix']}"

        # Make sure that doc_path has a path separator only if it exists (to avoid //)
        doc_path = context.get("doc_path", "")
        if doc_path and not doc_path.endswith("/"):
            doc_path = f"{doc_path}/"

        # Build the URL for "edit this button"
        url_edit = (
            f"{github_url}/{github_user}/{github_repo}"
            f"/edit/{github_version}/{doc_path}{file_name}"
        )
        return url_edit

    context["get_edit_url"] = get_edit_url

    # Ensure that the max TOC level is an integer
    context["theme_show_toc_level"] = int(context.get("theme_show_toc_level", 1))


# -----------------------------------------------------------------------------


def get_html_theme_path():
    """Return list of HTML theme paths."""
    theme_path = os.path.abspath(os.path.dirname(__file__))
    return [theme_path]


def setup(app):
    theme_path = get_html_theme_path()[0]
    app.add_html_theme("pydata_sphinx_theme", theme_path)
    app.set_translator("html", BootstrapHTML5Translator)

    # Read the Docs uses ``readthedocs`` as the name of the build, and also
    # uses a special "dirhtml" builder so we need to replace these both with
    # our custom HTML builder
    app.set_translator("readthedocs", BootstrapHTML5Translator, override=True)
    app.set_translator("readthedocsdirhtml", BootstrapHTML5Translator, override=True)
    app.connect("html-page-context", setup_edit_url)
    app.connect("html-page-context", add_toctree_functions)

    # Update templates for sidebar
    pkgdir = os.path.abspath(os.path.dirname(__file__))
    path_templates = os.path.join(pkgdir, "_templates")
    app.config.templates_path.append(path_templates)

    return {"parallel_read_safe": True, "parallel_write_safe": True}

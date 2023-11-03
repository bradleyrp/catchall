local lyaml   = require "lyaml"

-- SETTINGS
-- tags that are hidden 
hidden_tags = {["comment"]=true, ["hidden"]=true}
custom_figure_tag = 'custom_figure'
html_figure = [[
<p>
<a target="_blank" rel="noopener noreferrer" href="%s">
<img src="%s" alt="%s" 
style="max-width: 100%%;"></a><br>
<i>%s</i>
</p>
]]
-- via https://stackoverflow.com/a/45191209
-- the following is a bit sloppy in the markdown so we might use a simpler 
--   method set by the use_markdown_image_table
use_markdown_image_table = true
markdown_figure = [[
| ![%s](%s) |
|:--:| 
| *%s* |
]]

-- custom latex figures for beamer
-- dev: make the columns adjustable
custom_figure_left_tag = 'custom_figure_left'
beamer_figure_left = [[
\begin{columns}
\column{0.6\linewidth}
\centering
\begin{figure}
  \centering
  \includegraphics[max width=1.0\textwidth,max height=0.65\textheight]{%s}
  \caption{%s}
\end{figure}      
\column{0.4\linewidth}
%s
\end{columns} 
]]

custom_figure_pair_tag = 'custom_figure_pair'
beamer_figure_pair = [[
\begin{columns}
\column{0.5\linewidth}
\centering
\begin{figure}
  \centering
  \includegraphics[max width=1.0\textwidth,max height=0.65\textheight]{%s}
  \caption{%s}
\end{figure}      
\column{0.5\linewidth}
\begin{figure}
  \centering
  \includegraphics[max width=1.0\textwidth,max height=0.65\textheight]{%s}
  \caption{%s}
\end{figure}      
\end{columns} 
]]

beamer_figure = [[
\begin{figure}
  \centering
  \includegraphics[max width=1.0\textwidth,max height=0.6\textheight]{%s}
  \caption{%s}
\end{figure}  
]]

function find_pics (path)
  result = 'pics/' .. path
  return result
end

-- customizing paths for rendering on github-like platforms
function find_pics_md (path)
  result = '../pics/' .. path
  return result
end

if FORMAT:match 'html' then
  function CodeBlock (el)
    if el.classes[1] == custom_figure_tag then
      data = lyaml.load(el.text)
      path_abs = find_pics(data['path'])
      figure_src = string.format(
        html_figure,path_abs,path_abs,data['caption'],data['caption'])
      return pandoc.RawBlock('html', figure_src)
    elseif el.classes[1] == custom_figure_left_tag then
      data = lyaml.load(el.text)
      path_abs = find_pics(data['path'])
      if data["text"] == nil then
        error("custom figure got nil text")
      end
      figure_src = string.format(html_figure,
        path_abs,path_abs,data['caption'],data['caption'])
      inside_text_md = pandoc.read(data['text'],'markdown')
      inside_text_html = pandoc.write(inside_text_md,'html')
      return pandoc.RawBlock('html', figure_src .. "\n" .. inside_text_html)
    elseif el.classes[1] == custom_figure_pair_tag then
      data = lyaml.load(el.text)
      path_abs_0 = find_pics(data['path0'])
      path_abs_1 = find_pics(data['path1'])
      figure_src = string.format(html_figure,
        path_abs_0,path_abs_0,data['caption0'],data['caption0']) .. string.format(
        html_figure,
        path_abs_1,path_abs_1,data['caption1'],data['caption1'])
      return pandoc.RawBlock('html', figure_src .. "\n" .. inside_text_html)
    elseif hidden_tags[el.classes[1]] then
      return ""
    else
      return el
    end
  end
  function Meta(m)
    -- suppress metadata for the HTML target
    return {title=m.title}
  end
end

-- dev: removed: or FORMAT:match 'docx' then
if FORMAT:match 'markdown' then
  find_pics_this = find_pics_md
  function CodeBlock (el)
    if el.classes[1] == custom_figure_tag then
      data = lyaml.load(el.text)
      path_abs = find_pics_this(data['path'])
      -- selecting different methods to render the figure, since github does not
      --   make it possible to see captions. below we just tack it below so that
      --   the markdown is also readable
      if use_markdown_image_table then
        figure_src = string.format('![%s](%s)\n*%s*',data['caption'],
          path_abs,data['caption'])
      -- another method that uses a table which is cleaner but has a messy
      --   markdown file instead
      else
        figure_src = string.format(markdown_figure,
          data['caption'],path_abs,data['caption'])
      end
      out = pandoc.RawBlock('markdown', figure_src)
      return out
    elseif el.classes[1] == custom_figure_left_tag then
      data = lyaml.load(el.text)
      if data["text"] == nil then
        error("custom figure got nil text")
      end
      path_abs = find_pics_this(data['path'])
      -- selecting different methods to render the figure, since github does not
      --   make it possible to see captions. below we just tack it below so that
      --   the markdown is also readable
      if use_markdown_image_table then
        figure_src = string.format('![%s](%s)\n*%s*',data['caption'],
          path_abs,data['caption'])
      -- another method that uses a table which is cleaner but has a messy
      --   markdown file instead
      else
        figure_src = string.format(markdown_figure,
          data['caption'],path_abs,data['caption'])
      end
      return pandoc.RawBlock('markdown', figure_src .. "\n" .. data['text'])
    elseif el.classes[1] == custom_figure_pair_tag then
      data = lyaml.load(el.text)
      path_abs_0 = find_pics_this(data['path0'])
      path_abs_1 = find_pics_this(data['path1'])
      figure_src = string.format('![%s](%s)\n*%s*\n\n![%s](%s)\n*%s*',
        data['caption0'],path_abs_0,data['caption0'],
        data['caption1'],path_abs_1,data['caption1'])
      return pandoc.RawBlock('markdown', figure_src)
    elseif hidden_tags[el.classes[1]] then
      return ""
    else
      return el
    end
  end
  function Meta(m)
    -- suppress metadata for the github markdown target
    return {}
  end
end

if FORMAT:match 'docx' then
  find_pics_this = find_pics
  function CodeBlock (el)
    if el.classes[1] == custom_figure_tag then
      data = lyaml.load(el.text)
      path_abs = find_pics_this(data['path'])
      -- dev: no capations
      out = pandoc.Para({pandoc.Image({}, path_abs)})
      return out
    elseif hidden_tags[el.classes[1]] then
      return ""
    else
      return el
    end
  end
  function Meta(m)
    -- suppress metadata for the github markdown target
    return {}
  end
end

if FORMAT:match 'beamer' then
  function CodeBlock (el)
    if el.classes[1] == custom_figure_tag then
      data = lyaml.load(el.text)
      path_abs = find_pics(data['path'])
      figure_src = string.format(beamer_figure,
        path_abs,data['caption'])
      return pandoc.RawBlock('latex', figure_src)
    elseif el.classes[1] == custom_figure_left_tag then
      data = lyaml.load(el.text)
      path_abs = find_pics(data['path'])
      if data["text"] == nil then
        error("custom figure got nil text")
      end
      inside_text_md = pandoc.read(data['text'],'markdown')
      inside_text_latex = pandoc.write(inside_text_md,'latex')
      figure_src = string.format(beamer_figure_left,
        path_abs,data['caption'],inside_text_latex)
      return pandoc.RawBlock('latex', figure_src)
    elseif el.classes[1] == custom_figure_pair_tag then
      data = lyaml.load(el.text)
      print(data)
      -- could we make this a list with better names
      path_abs_0 = find_pics(data['path0'])
      path_abs_1 = find_pics(data['path1'])
      -- dev: need error handling
      figure_src = string.format(beamer_figure_pair,
        path_abs_0,data['caption0'],path_abs_1,data['caption1'])
      return pandoc.RawBlock('latex', figure_src)
    elseif hidden_tags[el.classes[1]] then
      return ""
    else
      return el
    end
  end
end

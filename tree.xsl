<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head>
        <title>Parse Tree Visualizer</title>
        <style>
          body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }
          .tree ul { padding-left: 20px; list-style-type: none; border-left: 1px dashed #555; }
          .tree li { margin: 5px 0; position: relative; }
          .tree li::before { content: "├── "; color: #555; }
          .node { background: #2d2d2d; padding: 3px 8px; border-radius: 4px; border: 1px solid #444; font-weight: bold; color: #4ec9b0; }
          .terminal { color: #ce9178; }
          .val { color: #dcdcaa; font-style: italic; }
        </style>
      </head>
      <body>
        <h2>Syntax Parse Tree</h2>
        <div class="tree">
          <ul><xsl:apply-templates/></ul>
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="*">
    <li>
      <span class="node">
        <xsl:if test="not(*)">terminal: </xsl:if>
        <xsl:value-of select="name()"/>
      </span>
      <xsl:if test="text() and normalize-space(text()) != ''">
        <span class="val"> = "<xsl:value-of select="text()"/>"</span>
      </xsl:if>
      <xsl:if test="*">
        <ul><xsl:apply-templates/></ul>
      </xsl:if>
    </li>
  </xsl:template>
</xsl:stylesheet>

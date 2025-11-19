## template_app.html

XXX_HEAD: head.html
XXX_H1: header.html
XXX_CONTROL_PANEL: control_panel.html
XXX_CY_CONTAINER: cy-container.html

## head.html

Unique variables:
XX_TITLE: title of the web page (Phenotype, Gene, or Gene List)
XX_JS_FILE_NAME: name of the JS file to be loaded (Phenotype, Gene, or network_genelist)


## header.html


if mode="Gene List":
    XX_TITLE = "gene list"
else:
    XX_TITLE = '''
    <a href="XXX_impc_url" target="_blank">XXX_mp_term_name_space</a>
    '''.replace("\n", "").strip()


## control-panel.html


XX_PHENOTYPE: insert control-panel-phenotype.html when mode="non-binary-phenotype"
remove it otherwise


### control-panel-phenotype.html

Effect-size slider

## cy-container.html


XX_PHENOTYPE: insert cy-container-phenotype.html when mode="non-binary-phenotype"
remove it otherwise


### cy-container-phenotype.html

Effect-size SVG scale bar

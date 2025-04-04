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


if mode="gene-symbols":
    XX_TITLE = "gene symbols"
else:
    XX_TITLE = '''
    <a href="XXX_impc_url" target="_blank">XXX_mp_term_name_space</a>
    '''.replace("\n", "").strip()


## control-panel.html


XX_PHENOTYPE: mode="non-binary-phenotype"のときにはcontrol-panel-phenotype.htmlを挿入
それ以外は削除


### control-panel-phenotype.html

効果量のスライダー

## cy-container.html


XX_PHENOTYPE: mode="non-binary-phenotype"のときにはcy-container-phenotype.htmlを挿入
それ以外は削除


### cy-container-phenotype.html

効果量のSVGスケールバー

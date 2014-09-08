var already_selected = []
$(function () {
    var tree = $("#jstree");

    tree.jstree();

    tree.bind("select_node.jstree", function (e, data) {
        // Desmarcamos los seleccionados
        already_selected.forEach(function (tag_id) {
            document.getElementById(tag_id).style.backgroundColor = 'initial';
        })

        var node_data = data["node"]["data"]["jstree"]
        if ("tag_list" in node_data) {

            // Marcamos los correspondientes nuevos
            if (node_data["tag_list"] != "") {
                already_selected = node_data["tag_list"].split(",")
                already_selected.forEach(function (tag_id) {
                    document.getElementById(tag_id).style.backgroundColor = '#FA5858';
                })
            } else {
                already_selected = []
            }

            $('#basic-modal-content').modal();

        }
        return data.instance.toggle_node(data.node);
    });

});

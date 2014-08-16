$(function () {
    var tree = $("#jstree");

    tree.jstree();

    tree.bind("select_node.jstree", function (e, data) {
        return data.instance.toggle_node(data.node);
    });

    tree.on("changed.jstree", function (e, data) {
        console.log(data.selected);
    });
});

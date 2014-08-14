$(function () {
    var tree = $("#jstree");

    tree.jstree();
    tree.on("changed.jstree", function (e, data) {
        console.log(data.selected);
    });
});

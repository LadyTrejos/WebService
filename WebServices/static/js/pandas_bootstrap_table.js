$('#datatable').bootstrapTable({
    striped: true,
    showColumns: true,
    showToggle: true,
    showExport: true,
    sortable: true,
    pagination: true,
    search: true,
    pageSize: 25,
    pageList: [10, 25, 50, 100, 'ALL'],
    columns: {{ columns|safe }},
    data: {{ data|safe }}
})
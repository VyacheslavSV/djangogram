$(document).ready(function () {
    $('.like-ajax').click(function (event) {
        event.preventDefault();
        var form = $(this).closest('form')
        var url = form.attr('action');
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            dataTypes: "json",
            context: this,
            success: function (response) {
                if (response.is_liked) {
                    $(this).text('Unlike');
                } else {
                    $(this).text('Like');
                }
                $(this).toggleClass('btn-danger');
                $(this).toggleClass('btn-success');
                $(this).next(".count_likes").text(response.likes_count);
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log(xhr.status + ': ' + xhr.statusText);
            }
        })
    })
})
$('.subscribe-ajax').click(function (event) {
    event.preventDefault();
    var form = $(this).closest('form')
    var url = form.attr('action');
    $.ajax({
        type: 'POST', url: url, data: form.serialize(), dataType: 'json', context: this, success: function (response) {
            if (response.is_subscribed) {
                $(this).text('Unsubscribed');
            } else {
                $(this).text('Subscribed');
            }
            $(this).toggleClass('btn-primary');
            $(this).toggleClass('btn-secondary');
        }, error: function (xhr, textStatus, errorThrown) {
            console.log(xhr.status + ': ' + xhr.statusText);
        }
    })

})

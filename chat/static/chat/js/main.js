// Show contacts or groups
$(document).ready(function () {
    $('.fa-users').hide();
    // const selectedOption = $("input[type='radio'][name='forContacts']")
    document.addEventListener('input', (e) => {
        if (e.target.getAttribute('name') === "forContacts") {
            if (e.target.value === 'contacts') {
                $('.contacts').show();
                $('.groups').hide();
                $('.fa-user-plus').show();
                $('.fa-users').hide();
            } else {
                $('.groups').show();
                $('.contacts').hide();
                $('.fa-users').show();
                $('.fa-user-plus').hide();
            }
        }
    });

    // Show the active user/group


    // Search functionality
    // $(function () {
    //     $('#searchbar').keyup(function () {
    //         $.ajax({
    //             type: "GET",
    //             url: "ws/chat/search/",
    //             data: {
    //                 'search_text': $('#searchbar').val(),
    //                 'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
    //             },
    //             success: searchSuccess,
    //             dataType: 'html'
    //         });
    //     });
    // });
    //
    // function searchSuccess(data, textStatus) {
    //     console.log(data);
    //     //$('#search-results').html(data);
    // }

    // Search functionality: again
    const user_input = $('#searchbar')
    const search_icon = $('#search-icon')
    const contacts_div = $('#search-results')
    const no_result = $('#no-result')

    no_result.hide()

    const endpoint = "/search/"
    const delay_by_in_ms = 500
    let scheduled_function = false

    let ajax_call = function (endpoint, request_parameters) {
        $.getJSON(endpoint, request_parameters)
            .done(response => {
                // fade out the artists_div, then:
                contacts_div.fadeTo('slow', 0).promise().then(() => {
                    // replace the HTML contents
                    contacts_div.html(response['html_from_view'])
                    // fade-in the div with new contents
                    contacts_div.fadeTo('slow', 1)
                    // stop animating search icon
                    search_icon.removeClass('blink')
                    no_result.show()
                })
            })
    }

    user_input.on('keyup', function () {
        const request_parameters = {
            // value of user_input: the HTML element with ID searchbar
            q: $(this).val()
        }
        console.log(request_parameters)

        // hide/show the current users and groups
        $('.normal-contacts').hide();
        $('.normal-groups').hide();

        // start animating the search icon with the CSS class
        search_icon.addClass('blink')
        no_result.addClass('no-result-found')

        // if scheduled_function is NOT false, cancel the execution of the function
        if (scheduled_function) {
            clearTimeout(scheduled_function)
        }

        // setTimeout returns the ID of the function to be executed
        scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
    })

    // The menu

    $('#action_menu_btn').click(function () {
        $('.action_menu').toggle();
    });


    $('.settings').click(function () {
        $('.show-settings').toggle();
    });

})


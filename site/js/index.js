$(document).ready(function(){

    $('select').material_select();

    $('#btnConjugate').click(function(){
        var params = {
            lang: $('#lang').first().val(),
            verb: $('#verb').first().val()
        };

        console.log(params);

        $.post('conjugate', params).done(onConjugationSucceeded)
                                   .fail(onConjugationFailed);
    });

    function onTranslationSucceeded(data) {

    }

    function onTranslationFailed() {

    }

    function onConjugationSucceeded(data) {
        var ul = $('<ul class="collapsible" data-collapsible="accordion"></ul>')

        data.conjugations.forEach(function(mode) {
            ul.append(createModeBlock(mode));
        });

        var conjugationsContainer = $('#conjugations');
        conjugationsContainer.empty();
        ul.css('display', 'none');
        ul.appendTo(conjugationsContainer).fadeIn('slow');

        $('.collapsible').collapsible({
            accordion: false
        });
    }

    function createModeBlock(mode) {
        var li = $('<li></li>');
        var header = $('<div class="collapsible-header"><i class="mdi-navigation-expand-more"></i></div>')
        var body = $('<div class="collapsible-body"></div>');

        header.append(mode.name);

        header.click(function () {
            var moreClass = 'mdi-navigation-expand-more';
            var lessClass = 'mdi-navigation-expand-less';

            var i = $(this).find('i');

            if (i.hasClass(moreClass)) {
                i.removeClass(moreClass);
                i.addClass(lessClass);
            }
            else {
                i.removeClass(lessClass);
                i.addClass(moreClass);
            }
        });

        li.append(header);
        li.append(body);

        mode.tenses.forEach(function(tense) {
            body.append(createTenseBlock(tense));
        });

        return li;
    }

    function createTenseBlock(tense) {
        //var title = $('<p></p>').append(tense.name);

        var table = $('<table class="hoverable"></table>').append(
            $('<thead></thead>'),
            $('<tbody></tbody>')
        );

        var names = tense.conjugations.every(function(conjugation) {
           return Boolean(conjugation.name);
        });

        if (Boolean(tense.name)) {
            $('thead', table).append(
                $('<tr></tr>').append(
                    $('<th data-field="tense-name"></th>').append(tense.name),
                    $('<th data-field="empty"></th>')
                )
            );
        }

        $('tbody', table).append(tense.conjugations.map(function(conjugation) {
            var tr = $('<tr></tr>');

            if (names) {
                tr.append($('<td></td>').append(conjugation.name));
            }

            tr.append($('<td></td>').append(conjugation.options.join(', ')));

            return tr;
        }));

        return $('<p></p>').append(table);
    }

    function onConjugationFailed() {
        console.log('Failed to conjugate');
    }

});
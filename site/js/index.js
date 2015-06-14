$(document).ready(function(){
    $('select').material_select();

    $('body').keydown(function(event) {
        if(event.keyCode === 13) {
            $('#btnConjugate').click();
        }
    });

    $('#btnConjugate').click(function(){
        var params = {
            lang: $('#lang').first().val(),
            verb: $('#verb').first().val(),
            translate: $('#translate').is(':checked')
        };

        if (params.verb.length === 0) {
            onNoInput();
            return;
        }

        setLoading();

        $.post('conjugate', params).done(onConjugationSucceeded)
                                   .fail(onConjugationFailed);
    });

    function onConjugationSucceeded(response) {
        console.log(response);

        if (!response.verbs ||
            !Array.isArray(response.verbs) ||
            response.verbs.length === 0) {
            onConjugationFailed();
        }
        else {
            processVerbs(response.verbs, response.fromEnglish);
        }
    }

    function processVerbs(verbs, fromEnglish) {
        if (fromEnglish) {
            var col = $('<div class="col s12"></div>');
            var tabSize = Math.min(12 / verbs.length, 3);
            var tabClass = '"tab col s' + tabSize + '"';
            var tabs = $('<ul class="tabs"></ul>');

            verbs.forEach(function(verb, index) {
                var href = '"#verb' + index + '"';
                var aClass = index === 0 ? '"active"' : '""';
                var link =  $('<a class=' + aClass + ' href=' + href + '></a>');

                link.append(verb.verb);

                tabs.append(
                    $('<li class=' + tabClass + '></li>').append(
                        link
                    )
                );

                link.click(function() {
                   enableCollapsible();
                });
            });

            col.append(tabs);

            updateConjugationsContainer(col);

            verbs.forEach(function(verb, index) {
                var id = '"verb' + index + '"';
                $('#conjugations').append(
                    $('<div class="col s12" id=' + id + '></div>').append(
                        processConjugations(verb.conjugations)
                    )
                );
            });

        }
        else {
            var conjugationsList = processConjugations(verbs[0].conjugations);
            updateConjugationsContainer(conjugationsList);
        }
    }

    function processConjugations(conjugations) {
        var ul = $('<ul class="collapsible" data-collapsible="accordion"></ul>');

        conjugations.forEach(function(mode) {
            ul.append(createModeBlock(mode));
        });

        return ul;
    }

    function createModeBlock(mode) {
        var li = $('<li></li>');
        var header = $('<div class="collapsible-header"><i class="mode-expander mdi-navigation-expand-more"></i></div>')
        var body = $('<div class="collapsible-body"></div>');

        header.append(mode.name);

        header.click(function () {
            $('.mode-expander').each(function(index, expander){
                expander = $(expander);

                var currentName = expander.parent().text();
                var moreClass = 'mdi-navigation-expand-more';
                var lessClass = 'mdi-navigation-expand-less';

                if (currentName !== mode.name || expander.hasClass(lessClass)) {
                    expander.removeClass(lessClass);
                    expander.addClass(moreClass);
                }
                else {
                    expander.removeClass(moreClass);
                    expander.addClass(lessClass);
                }
            });
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

    function onNoInput() {
        setErrorMessage("Please enter a verb before looking for conjugations.");
    }

    function onConjugationFailed() {
        var errorMsg = "Sorry, we couldn't find any conjugations for that" +
            " verb. Make sure to use the infinitive.";

        setErrorMessage(errorMsg);
    }

    function setErrorMessage(message) {
        var errorBlock = $('<div class="col"></div>').append(
            $('<div class="card-panel red darken-4"></div>').append(
                $('<div class="row"></div>').append(
                    $('<div class="col l2"></div>').append(
                        $('<i class="medium mdi-alert-error"></i>')
                    ),
                    $('<div class="col l10"></div>').append(
                        $('<div class="valign-wrapper"></div>').append(
                            $('<p class="valign"></p>').append(
                                $('<span class="white-text"></span>').append(message)
                            )
                        )
                    )
                )
            )
        );

        updateConjugationsContainer(errorBlock);
    }

    function setLoading() {
        var loadingBlock = $('<div class="col l2 offset-l5"></div>').append(
            $('<div class="row"></div>').append(
                $('<div class="preloader-wrapper big active"></div>').append(
                    $('<div class="spinner-layer spinner-blue-only"></div>').append(
                        $('<div class="circle-clipper left"></div>').append(
                            $('<div class="circle"></div>')
                        ),
                        $('<div class="circle-clipper right"></div>').append(
                            $('<div class="circle"></div>')
                        )
                    )
                )
            )
        );

        updateConjugationsContainer(loadingBlock);
    }

    function updateConjugationsContainer(element) {
        var conjugationsContainer = $('#conjugations');
        conjugationsContainer.empty();
        element.css('display', 'none');
        element.appendTo(conjugationsContainer).fadeIn('slow');

        enableCollapsible();

        $('ul.tabs').tabs();
    }

    function enableCollapsible() {
        $('.collapsible').collapsible({
            accordion: false
        });
    }
});
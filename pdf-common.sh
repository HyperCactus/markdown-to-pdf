# Shared build diagnostics for md2pdf and ipynb2pdf (sourced by Bash).

cleanup_build() {
    if [[ "$KEEP_BUILD" == true ]]; then
        printf '%s: build files retained at %s\n' "$PROGRAM_NAME" "$BUILD_DIR" >&2
    else
        rm -rf "$BUILD_DIR"
    fi
}

conversion_failed() {
    local stage="$1" details="$2"
    KEEP_BUILD=true
    [[ -t 1 ]] && printf '\n' >&2
    printf '%s: error: %s failed\n' "$PROGRAM_NAME" "$stage" >&2
    if grep -Eq '^!|^.*\.(tex|sty):[0-9]+:' "$details"; then
        # Read the complete log; head under pipefail can otherwise hide the
        # original error behind a SIGPIPE failure.
        awk '/^!|^.*\.(tex|sty):[0-9]+:/ && !found { found=1; remaining=8 } remaining > 0 { print; remaining-- }' "$details" >&2
    else
        tail -n 25 "$details" >&2
    fi
    printf '%s: full diagnostics: %s\n' "$PROGRAM_NAME" "$details" >&2
    exit 1
}

check_pdf() {
    local pattern label
    for pattern in 'Overfull \\hbox' 'Missing character:'; do
        if [[ "$pattern" == 'Missing character:' ]]; then
            label="missing font characters"
        else
            label="content extends beyond the page margin"
        fi
        if grep -q "$pattern" "$LOG"; then
            KEEP_BUILD=true
            [[ -t 1 ]] && printf '\n' >&2
            printf '%s: warning: %s\n' "$PROGRAM_NAME" "$label" >&2
            grep "$pattern" "$LOG" >&2
            if [[ "$STRICT" == true ]]; then
                conversion_failed "PDF quality check (--strict)" "$LOG"
            fi
        fi
    done
    [[ -s "$PDF" ]] || conversion_failed "PDF output validation" "$BUILD_LOG"
}

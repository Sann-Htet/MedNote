<script lang="ts">
  import type {
    SoapJsonType,
    GenericJson,
    Content,
    Entity,
    ExtractedEntities,
  } from "$lib/types/mednote";
  import { extractEntity } from "$lib/api/mednote";
  import { colors } from "../../entityLegend";
  import { onMount, afterUpdate } from "svelte";

  import { showEntityLabelStore, isEntityDetectionStore, isEntittDetectionLoadingStore } from "$lib/stores/EntityDetectionStore";

  export let soap_json: SoapJsonType;

  let input: GenericJson = soap_json["SOAP_Note"];
  if (input == null) {
    input = soap_json;
  }
  let sections = Object.keys(input);
  let extractedEntities: ExtractedEntities | null = null;

  $: {
    if ($isEntityDetectionStore) {
      try {
        if (extractedEntities == null) {
          isEntittDetectionLoadingStore.set(true);
          (async () => {
            extractedEntities = await extractEntity(soap_json);
            console.log(Object.keys(extractedEntities).length <= 0);
            console.log("extractedEntities", extractedEntities);
            sections = Object.keys(extractedEntities);
            isEntittDetectionLoadingStore.set(false);
          })();
        }
      } catch (error) {
        console.error(error);
      }
    } else {
      extractedEntities = null;
    }
  }
  onMount(async () => {});

  $: if ($showEntityLabelStore !== undefined) {
    updateDynamicClasses();
  }

  function updateDynamicClasses() {
    const elements = document.querySelectorAll(".entityLabel");
    elements.forEach((el) => {
      el.classList.toggle("hidden", !$showEntityLabelStore);
    });
  }

  function colorizeText(text: string, entities: Entity[]): string {
    if (entities.length <= 0) return text;
    let result = text;
    let currentIndex = 0;

    entities.forEach((entity) => {
      const { start, end, entity_group } = entity;
      const color = colors[entity_group];
      const classAttribute = ` class="entityLabel hidden entity font-bold uppercase align-middle ml-2 bg-white p-1 rounded border border-darkgrey border-opacity-10"`;
      const spanStart = `<span style="background-color: ${color};">`;
      // const spanEnd =`</span>`;
      const spanEnd = ` <span
        ${classAttribute}
        style="font-size: 9px;">${entity_group.replace("_", " ")}</span
      ></span>`;

      const adjustedStart = start + currentIndex;
      const adjustedEnd = end + currentIndex;

      // Update the result string by replacing the plain text with styled spans
      result =
        result.slice(0, adjustedStart) +
        spanStart +
        result.slice(adjustedStart, adjustedEnd) +
        spanEnd +
        result.slice(adjustedEnd);

      // Update the current index to account for the added characters
      currentIndex += spanStart.length + spanEnd.length;
    });

    return result;
  }

  let getSectionContent = (section: string) => {
    let content: Content[] = [];
    const parseContent = (data: any, parentKey = "") => {
      for (let key in data) {
        if (typeof data[key] !== "string") {
          parseContent(data[key], key);
        } else {
          content.push({
            title: parentKey
              ? `${parentKey.replace(/[_-]/g, " ")} - ${key}`.replace(
                  /[_-]/g,
                  " ",
                )
              : key,
            content: data[key],
          });
        }
      }
    };
    parseContent(input[section]);
    return content;
  };

  function getTextAndEntities(
    data: any,
    parentKey: string = "",
  ): { subTittle: string; text: string; entities: any[] }[] {
    let results: { subTittle: string; text: string; entities: any[] }[] = [];

    if (typeof data === "object" && data !== null) {
      // Checking if 'text' and 'entities' properties exist at this level
      if ("text" in data && "entities" in data) {
        const { text, entities } = data;
        results.push({ subTittle: parentKey, text, entities });
      } else {
        // If don't exist, recursively search deeper
        for (const key in data) {
          if (Object.hasOwnProperty.call(data, key)) {
            const value = data[key];
            // parent key is the subtitle of the data
            const subResults = getTextAndEntities(value, (parentKey = key));
            results = results.concat(subResults);
          }
        }
      }
    }

    return results;
  }

  function getColorizedSectionContent(
    parentKey: string,
  ): { title: string; content: string }[] {
    if (extractedEntities == null) return [];

    const parentContent = extractedEntities[parentKey];
    console.log("parentContent", parentContent);
    const result: { title: string; content: string }[] = [];

    if (parentContent && typeof parentContent === "object") {
      //  two-parent-key data structure
      if ("text" in parentContent && "entities" in parentContent) {
        const { text, entities } = parentContent;
        let highlightedText: string = "";

        if (Array.isArray(entities)) {
          console.log("GOt ere");
          highlightedText = colorizeText(text + "", entities);
        }

        result.push({ title: parentKey, content: highlightedText });
      } else {
        // Iterate through the keys if it is a three-parent-key data structure
        for (const sectionKey in parentContent) {
          if (Object.hasOwnProperty.call(parentContent, sectionKey)) {
            const section = parentContent[sectionKey];
            const output = getTextAndEntities(section);
            let reportCount = 1;
            output.forEach(({ subTittle, text, entities }) => {
              const capitalizedString = subTittle.toLocaleUpperCase();
              let uniqueSubTitle =
                sectionKey === capitalizedString
                  ? sectionKey
                  : sectionKey + " " + subTittle;

              let highlightedText: string = "";

              if (Array.isArray(entities)) {
                highlightedText = colorizeText(text + "", entities);
              }
              result.push({
                title: uniqueSubTitle,
                content: highlightedText,
              });
              ++reportCount;
            });
          }
        }
      }
    }
    return result;
  }
</script>

<h1 class="text-3xl font-bold text-center mb-5">SOAP Note Report</h1>

{#if extractedEntities !== null}
  {#each sections as section}
    <h2 class="text-2xl font-semibold mt-5 mb-3">
      {section.replace(/[_-]/g, " ")}
    </h2>
    {#each getColorizedSectionContent(section) as item}
      <div>
        <h3 class="text-lg font-semibold ml-2 mt-3">
          {item.title.replace(/[_-]/g, " ")}
        </h3>
        <p class="text-base ml-2 mb-5">
          {@html item.content}
        </p>
      </div>
    {/each}
  {/each}
{:else}
  {#each sections as section}
    <h2 class="text-2xl font-semibold mt-5 mb-3">
      {section.replace(/[_-]/g, " ")}
    </h2>
    {#each getSectionContent(section) as item}
      <div>
        <h3 class="text-lg font-semibold ml-2 mt-3">
          {item.title.replace(/[_-]/g, " ")}
        </h3>
        <p class="text-base ml-2 mb-5">
          {@html item.content}
        </p>
      </div>
    {/each}
  {/each}
{/if}

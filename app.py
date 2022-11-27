import pandas as pd
import numpy as np
import myharmonizer.myharmonizer as mh
import streamlit as st
import json
import io
import streamlit_ext as ste

examples_json = st.selectbox('Please select json example:',('None', 'SEQC', 'Multi-tissue', 'Multi-cell line'))
examples_excel = st.selectbox('Please select excel example:',('None', 'SEQC', 'Multi-tissue', 'Multi-cell line'))
meta_json = st.file_uploader("Upload Meta Json File:")

input_data = st.file_uploader("Upload Meta Data (Excel/CSV) File:")

if meta_json != None or examples_json != 'None':
    match examples_json:
        case 'Multi-cell line':
            toy_mH = mh.myHarmonizer('examples/myHarmonizer-cells.json')
        case 'SEQC':
            toy_mH = mh.myHarmonizer('examples/myHarmonizer-seqc.json')
        case 'Multi-tissue':
            toy_mH = mh.myHarmonizer('examples/myHarmonizer-tissue.json')
        case _:
            json.dump(json.load(meta_json), open('myHarmonizer.json','w'))
            # Build toy myHarmonizer
            toy_mH = mh.myHarmonizer('myHarmonizer.json')
    # Get a shortened feature list for the toy dataset
    rawfeatures = toy_mH.modelmeta['encoder_metrics']['features']

# Generate 5 random samples
    if input_data != None or examples_excel != 'None':
        match examples_json:
            case 'Multi-cell line':
                newdata = pd.read_csv('examples/cells-test.csv')
            case 'SEQC':
                newdata = pd.read_csv('examples/seqc-test.csv')
            case 'Multi-tissue':
                newdata = pd.read_csv('examples/tissue-test.csv')
            case _:
                if input_data.name.split('.')[-1] == 'csv':
                    newdata = pd.read_csv(input_data)
                else:
                    newdata = pd.read_excel(input_data)
        index_col = newdata.columns[0]
        if newdata[index_col].duplicated().sum() > 0:
            st.error("Check " + index_col + " column : deduplicate values. Remove and reupload the correct excel file")
        else:
            newdata = newdata.set_index(index_col)

            transformeddata = toy_mH.transform(newdata)
            metric_option = st.selectbox('Which metric usage?',('Pearson', 'Spearman', 'CCC', 'Euclidean', 'Manhattan', 'Cosine'))
            print(metric_option)
            pearson_sim = mh.similarity(transformeddata, toy_mH.data, metric=metric_option)
                
            # Examine metadata in myHarmonizer object
            #toy_mH.metadata
            pearson_sim

            ste.download_button('Download CSV file:', toy_mH.metadata.to_csv(index=False), file_name='metadata.csv', mime='text/csv')
            metadata_option = st.selectbox('Which metadata usage?',tuple(toy_mH.metadata.columns))
            # Plot heatmap
            fig1 = mh.heatmap(pearson_sim, toy_mH, user_metadata=None, kb_metadata=metadata_option)
            st.pyplot(fig1)
            img = io.BytesIO()
            fig1.savefig(img, format='png')
            ste.download_button('Download graph image:', data=img, file_name='heatmap.png', mime='image/png')